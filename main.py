from typing import List

import math
import pygame
import sys

from colors import *
from data import Arduino


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
        ppx = self.k[0] * self.size[0] / X   # pixel per Absolute x
        ppy = self.k[1] * self.size[1] / Y   # pixel per Absolute y

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

        self.a = Arduino()

        self.sync = 120

    def find(self, data: List[int]):
        i = 0
        while data[i] > self.sync:
            i += 1
            if i == len(data):
                return 0

        while data[i] < self.sync:
            i += 1
            if i == len(data):
                return 0

        return i

    def render(self):
        data, one_measure_time = self.a.read_data()
        if 0 == one_measure_time:
            return

        i = self.find(data)
        data = data[i:]

        self.osc.coord[0] = one_measure_time * 900

        self.osc.line((0, 250, 250),
                      (0, self.sync),
                      (self.osc.coord[0], self.sync))

        t = math.log(self.osc.coord[0]) / math.log(10)
        t = int(t)
        one = 10 ** (t - 1)

        for i in range(10):
            self.osc.line((100, 100, 100),
                          (one * i * 10, 0),
                          (one * i * 10, self.osc.coord[1]))

            self.osc.text((one * i * 10, self.osc.coord[1]),
                          "{:.1f}".format(one * i / 1000))

        it_p = iter(data)
        it_c = iter(data)
        next(it_c)
        for i, (p, n) in enumerate(zip(it_p, it_c)):
            self.osc.line((0, 255, 0),
                          (i * one_measure_time, p + 1),
                          ((i + 1) * one_measure_time, n + 1))

    def update(self):
        self.screen.blit(self.osc.surface, (0, 0))
        pygame.display.update()
        self.osc.clear()

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS: self.sync -= 1
                if event.key == pygame.K_EQUALS: self.sync += 1


class _Display:
    def __init__(self):
        pygame.init()

        self.size = (1000, 400)
        self.screen = pygame.display.set_mode(self.size)
        self.a = Arduino()
        self.start = 40
        self.k = [1, 0.5]

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.font = pygame.font.SysFont('Verdana', 20)

    def text(self, pos, text):
        textsurface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(textsurface, pos)

    def find(self, data: List[int]):
        i = 0
        while data[i] > self.start:
            i += 1
            if i == len(data):
                return 0

        while data[i] < self.start:
            i += 1
            if i == len(data):
                return 0

        return i

    def line(self, color, a, b):
        pygame.draw.line(self.screen, color, a, b)

    def render(self):
        data, one_measure_time = self.a.read_data()
        if 0 == one_measure_time:
            return
        i = self.find(data)
        data = data[i:]

        it_p = iter(data)
        it_c = iter(data)
        next(it_c)

        # draw 
        ms = 2
        ms_in_px = ms * 1000 / one_measure_time

        for i in range(10):
            self.line((100, 100, 100), (ms_in_px * i * self.k[1], 0),
                      (ms_in_px * i * self.k[1], 400))
            self.text((ms_in_px * i * self.k[1], 0), str(ms * i))

        self.line((0, 250, 250), (0, (300 - self.start) * self.k[0]),
                  (1000, (300 - self.start) * self.k[0]))

        for i, (p, n) in enumerate(zip(it_p, it_c)):
            self.line((0, 255, 0), (i * self.k[1], (300 - p) * self.k[0]),
                      ((i + 1) * self.k[1], (300 - n) * self.k[0]))

    def update(self):
        pygame.display.update()
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, *self.size))

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS: self.start -= 1
                if event.key == pygame.K_EQUALS: self.start += 1


d = Display()

while True:
    d.main()
    d.render()
    d.update()
