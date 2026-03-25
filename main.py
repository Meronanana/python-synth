import pygame
import sounddevice as sd

from config import FS, BLOCK
from waveforms import CURRENT_WAVEFORM, handle_waveform_key
from synth import (
    audio_callback, start_note, release_note,
    lock, notes, chord_loop,
)
from chord_loop import CHORD_NAMES


def main():
    pygame.init()
    screen = pygame.display.set_mode((520, 230))
    pygame.display.set_caption("Mini Synth : ESC to quit")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    running = True

    with sd.OutputStream(
        samplerate=FS,
        channels=1,
        dtype="float32",
        blocksize=BLOCK,
        callback=audio_callback,
    ):
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Space로 코드 루프 토글
                    if event.key == pygame.K_SPACE:
                        with lock:
                            chord_loop.toggle()

                    # 숫자 키(1~5)로 파형 변경
                    handle_waveform_key(event.key)

                    # 건반 키면 노트 시작
                    start_note(event.key)

                elif event.type == pygame.KEYUP:
                    release_note(event.key)

            # UI
            screen.fill((18, 18, 18))

            # 코드 루프 상태
            with lock:
                if chord_loop.active:
                    ci = chord_loop.current_chord_index()
                    loop_status = f"Loop: ON  [{' > '.join(('*'+c+'*' if i==ci else c) for i,c in enumerate(CHORD_NAMES))}]"
                else:
                    loop_status = "Loop: OFF (Space to start)"

            from waveforms import CURRENT_WAVEFORM as cw
            lines = [
                "Hold keys to sustain, release to fade out",
                "Waveform: 1=sine  2=square  3=saw  4=triangle  5=pulse25",
                f"Current waveform: {cw.name}",
                loop_status,
                "Quit: ESC or close window",
            ]
            y = 40
            for s in lines:
                surf = font.render(s, True, (230, 230, 230))
                screen.blit(surf, (30, y))
                y += 30

            # show active
            with lock:
                active = []
                for k, n in notes.items():
                    if not n.releasing and n.gain > 1e-3:
                        active.append(pygame.key.name(k))
                active_text = "Active: " + (", ".join(active) if active else "-")

            surf = font.render(active_text, True, (200, 200, 200))
            screen.blit(surf, (30, 170))

            pygame.display.flip()
            clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
