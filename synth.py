import numpy as np
import pygame
import threading

from config import *
from waveforms import osc, CURRENT_WAVEFORM
from chord_loop import ChordLoop

KEY_TO_MIDI = {
    pygame.K_a: 60,  # C4 (도)
    pygame.K_w: 61,  # C#4 (도#)
    pygame.K_s: 62,  # D4 (레)
    pygame.K_e: 63,  # D#4 (레#)
    pygame.K_d: 64,  # E4 (미)
    pygame.K_f: 65,  # F4 (파)
    pygame.K_t: 66,  # F#4 (파#)
    pygame.K_g: 67,  # G4 (솔)
    pygame.K_y: 68,  # G#4 (솔#)
    pygame.K_h: 69,  # A4 (라)
    pygame.K_u: 70,  # A#4 (라#)
    pygame.K_j: 71,  # B4 (시)
    pygame.K_k: 72,  # C5 (도)
}


def midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


class Note:
    __slots__ = ("freq", "phase", "gain", "releasing")
    def __init__(self, freq: float):
        self.freq = freq
        self.phase = 0.0
        self.gain = 0.0
        self.releasing = False


notes: dict[int, Note] = {}  # pygame key -> Note
lock = threading.Lock()
chord_loop = ChordLoop()


def audio_callback(outdata, frames, time_info, status):
    from waveforms import CURRENT_WAVEFORM

    block = np.zeros(frames, dtype=np.float32)

    with lock:
        dead = []
        for k, n in notes.items():
            # envelope
            if n.releasing:
                n.gain = max(0.0, n.gain - RELEASE_STEP)
            else:
                n.gain = min(1.0, n.gain + ATTACK_STEP)

            # oscillator (파형 생성)
            phase_inc = (2.0 * np.pi * n.freq) / FS
            idx = np.arange(frames, dtype=np.float32)
            phases = n.phase + phase_inc * idx

            # 선택된 파형으로 블록에 더하기
            wave = osc(phases, CURRENT_WAVEFORM)
            block += (wave * n.gain).astype(np.float32)

            n.phase = float(phases[-1] + phase_inc) % (2.0 * np.pi)

            if n.releasing and n.gain <= 1e-4:
                dead.append(k)

        for k in dead:
            notes.pop(k, None)

    # 백그라운드 코드 루프 믹싱
    block += chord_loop.render(frames)

    block = np.clip(block, -1.0, 1.0) * MASTER_GAIN
    outdata[:] = block.reshape(-1, 1)


def start_note(pg_key):
    midi = KEY_TO_MIDI.get(pg_key)
    if midi is None:
        return
    with lock:
        if pg_key not in notes:
            notes[pg_key] = Note(midi_to_freq(midi))
        else:
            notes[pg_key].releasing = False


def release_note(pg_key):
    if pg_key not in KEY_TO_MIDI:
        return
    with lock:
        n = notes.get(pg_key)
        if n is not None:
            n.releasing = True
