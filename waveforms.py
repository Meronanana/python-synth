from abc import ABC, abstractmethod

import numpy as np
import pygame

from config import *


class Waveform(ABC):
    """파형 인터페이스. 커스텀 파형을 만들려면 이 클래스를 상속하세요."""

    @property
    @abstractmethod
    def name(self) -> str:
        """파형 이름 (UI 표시용)."""
        ...

    @abstractmethod
    def generate(self, phases: np.ndarray) -> np.ndarray:
        """
        라디안 단위 phases 배열을 받아 -1.0 ~ 1.0 범위의 샘플을 반환합니다.
        """
        ...

    def __repr__(self) -> str:
        return self.name


class SineWave(Waveform):
    @property
    def name(self) -> str:
        return "sine"

    def generate(self, phases: np.ndarray) -> np.ndarray:
        return np.sin(phases)


class SquareWave(Waveform):
    @property
    def name(self) -> str:
        return "square"

    def generate(self, phases: np.ndarray) -> np.ndarray:
        return np.sign(np.sin(phases))


class SawWave(Waveform):
    @property
    def name(self) -> str:
        return "saw"

    def generate(self, phases: np.ndarray) -> np.ndarray:
        saw = (phases / (2.0 * np.pi)) % 1.0
        return 2.0 * saw - 1.0


class TriangleWave(Waveform):
    @property
    def name(self) -> str:
        return "triangle"

    def generate(self, phases: np.ndarray) -> np.ndarray:
        saw = (phases / (2.0 * np.pi)) % 1.0
        return 2.0 * np.abs(2.0 * saw - 1.0) - 1.0


class CustomWaveform(Waveform):
    """커스텀 파형: 펄스 웨이브 (듀티 사이클 25%) — 레트로 게임 사운드 느낌"""

    @property
    def name(self) -> str:
        return "pulse25"

    def generate(self, phases: np.ndarray) -> np.ndarray:
        cycle = (phases / (2.0 * np.pi)) % 1.0
        return np.where(cycle < 0.25, 1.0, -1.0)


# 파형 레지스트리: 숫자 키 -> Waveform 인스턴스
WAVEFORMS: dict[int, Waveform] = {
    pygame.K_1: SineWave(),
    pygame.K_2: SquareWave(),
    pygame.K_3: SawWave(),
    pygame.K_4: TriangleWave(),
    pygame.K_5: CustomWaveform(),
}

CURRENT_WAVEFORM: Waveform = WAVEFORMS[pygame.K_1]  # 기본: sine


def osc(phases: np.ndarray, waveform: Waveform = None) -> np.ndarray:
    """선택된 Waveform 인스턴스로 파형을 생성합니다."""
    if waveform is None:
        waveform = CURRENT_WAVEFORM
    return waveform.generate(phases)


def handle_waveform_key(pg_key: int) -> None:
    """숫자 키를 눌렀을 때 파형을 변경하는 함수."""
    global CURRENT_WAVEFORM
    new_wave = WAVEFORMS.get(pg_key)
    if new_wave is not None:
        CURRENT_WAVEFORM = new_wave
