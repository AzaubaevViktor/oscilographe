from typing import List

import math
import pygame
import sys

from colors import *
from data import Arduino
from signal_processor import SignalProcessor

_keys = {
	pygame.K_0: 0,
	pygame.K_1: 1,
	pygame.K_2: 2,
	pygame.K_3: 3,
	pygame.K_4: 4,
	pygame.K_5: 5,
	pygame.K_6: 6,
	pygame.K_7: 7,
}

class Area:
    def __init__(self,
                 size,
                 coord=(1, 1),
                 k=(1, 1),
                 pos=None):
        """
        :param size: Размер области
        :param k: Коэффициенты увеличения
        :param coord: Абсолютные координаты
        :param pos: Смещение в абсолютных координатах
        | coord[1]
        |
        |_________________ coord[0]
        (0, 0)
        """
        self.size = size
        self.k = k
        self.surface = pygame.Surface(self.size)
        self.coord = list(coord)
        self.pos = list(pos or (0, 0))
        self.font = pygame.font.SysFont('Ubuntu Mono', 14)

    def clear(self, color=BLACK):
        self.surface.fill(color)

    def _convert(self, point):
        """
        X = coord[0]
        |
        |
        |
        |-------------------p (x, y)
        |                   |
        |                   |
        |                   |
        |___________________|___________Y = coord[1]
        """
        X, Y = self.coord

        cpx, cpy = (self.pos[0] + point[0]) / X, (self.pos[1] + point[1]) / Y
        cx, cy = self.size[0] * cpx, self.size[1] * cpy  # Center x & y in pixel

        return cx, self.size[1] - cy

    def line(self, color, a, b):
        pygame.draw.line(self.surface, color,
                         self._convert(a), self._convert(b))

    def text(self, point, text):
        textsurface = self.font.render(text, True, (255, 255, 255))
        self.surface.blit(textsurface, self._convert(point))


class Display:
    def __init__(self):
        pygame.init()

        self.size = (1000, 400)
        self.screen = pygame.display.set_mode(self.size)
        self.osc = Area(self.size, coord=(10, 257))  # 10ms, 256 values

        self.signal_processor = SignalProcessor(120, True)

        self.a = Arduino()

    def render(self):
        data, one_measure_time = self.a.read_data()
        if 0 == one_measure_time:
            return

        signal = self.signal_processor.calc(data, one_measure_time)

        self.osc.coord[0] = one_measure_time * 900
        self.osc.pos[0] = self.osc.coord[0] / 2

        self.osc.line((0, 250, 250),
                      (-self.osc.coord[0] / 2, self.signal_processor.sync_level),
                      (self.osc.coord[0] / 2, self.signal_processor.sync_level))

        t = math.log(self.osc.coord[0]) / math.log(10)
        t = int(t)
        one = 10 ** (t - 1)

        for i in range(-10, 10):
            color = (100, 100, 100) if i else (200, 200, 200)
            self.osc.line(color,
                          (one * i * 10, 0),
                          (one * i * 10, self.osc.coord[1]))

            self.osc.text((one * i * 10, self.osc.coord[1]),
                          "{:.1f}".format(one * i / 1000))

        it_p = iter(data)
        it_c = iter(data)
        next(it_c)
        for i, (p, n) in enumerate(zip(it_p, it_c)):
            j = i - signal.sync_index
            self.osc.line((0, 255, 0),
                          (j * one_measure_time, p + 1),
                          ((j + 1) * one_measure_time, n + 1))

    def update(self):
        self.screen.blit(self.osc.surface, (0, 0))
        pygame.display.update()
        self.osc.clear()

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS: self.signal_processor.sync_level -= 1
                if event.key == pygame.K_EQUALS: self.signal_processor.sync_level += 1
                number = _keys.get(event.key, None)
                if number:
                    self.a.set_divider(number)

d = Display()

while True:
    d.main()
    d.render()
    d.update()
