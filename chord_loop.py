import numpy as np

from config import FS
from waveforms import SineWave, Waveform

# ----------------------------
# Background chord loop
# ----------------------------
BPM = 120
BEATS_PER_BAR = 4
BARS = 4
SECONDS_PER_BEAT = 60.0 / BPM
SECONDS_PER_BAR = SECONDS_PER_BEAT * BEATS_PER_BAR
LOOP_LENGTH = SECONDS_PER_BAR * BARS  # 총 루프 길이 (초)

# 4마디 코드 진행: C → Am → F → G  (각 1마디)
CHORD_PROGRESSION = [
    [60, 64, 67],       # C  (도미솔)
    [57, 60, 64],       # Am (라도미)
    [53, 57, 60],       # F  (파라도)
    [55, 59, 62],       # G  (솔시레)
]

CHORD_NAMES = ["C", "Am", "F", "G"]

LOOP_WAVEFORM: Waveform = SineWave()
LOOP_GAIN = 0.12  # 백그라운드이므로 작게


def midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


class ChordLoop:
    """백그라운드 코드 루프 상태 관리"""
    def __init__(self):
        self.active = False
        self.time_pos = 0.0  # 루프 내 현재 위치(초)
        self.phases: dict[int, float] = {}  # midi -> phase

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.time_pos = 0.0
            self.phases.clear()

    def current_chord_index(self) -> int:
        return int(self.time_pos / SECONDS_PER_BAR) % BARS

    def render(self, frames: int) -> np.ndarray:
        if not self.active:
            return np.zeros(frames, dtype=np.float32)

        chord_idx = self.current_chord_index()
        midi_notes = CHORD_PROGRESSION[chord_idx]

        block = np.zeros(frames, dtype=np.float32)
        for midi in midi_notes:
            freq = midi_to_freq(midi)
            phase = self.phases.get(midi, 0.0)
            phase_inc = (2.0 * np.pi * freq) / FS
            idx = np.arange(frames, dtype=np.float32)
            phases_arr = phase + phase_inc * idx
            wave = LOOP_WAVEFORM.generate(phases_arr)
            block += wave.astype(np.float32)
            self.phases[midi] = float(phases_arr[-1] + phase_inc) % (2.0 * np.pi)

        # 시간 전진 & 루프
        self.time_pos += frames / FS
        if self.time_pos >= LOOP_LENGTH:
            self.time_pos -= LOOP_LENGTH

        return block * LOOP_GAIN
