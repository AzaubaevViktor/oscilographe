import operator
from functools import reduce
from typing import List


class MyList(list):
    def __sub__(self, other: list):
        return MyList(map(lambda x: operator.sub(*x), zip(self, other)))

    def __le__(self, value):
        return MyList(map(lambda x: operator.le(x, value), self))



def sq(l):
    return reduce((lambda x, y: x + y ** 2), l)


class Signal:
    def __init__(self, data: List[int], hz: float):
        self.data = data
        self.hz = hz
        self.sync_index = None
        self.freq = 0

    def __getitem__(self, item) -> int:
        return self.data[item]

    def __iter__(self):
        return iter(self.data)


class SignalProcessor:
    def __init__(self, sync_level, sync_front_up=True):
        self.sync_level = sync_level
        self.sync_front_up = sync_front_up

    def calc(self, data, ms_per_measure):
        signal = Signal(data, 1/ ms_per_measure)

        signal.sync_index = self._find_sync(signal)

        # period = self._get_period(signal.data)

        signal.freq = 0
        if 0:
            signal.freq = 1 / (period / signal.hz / 100000)

        return signal

    def _find_sync(self, signal: Signal):
        s = signal
        mid_index = len(s.data) // 2
        for i in range(mid_index - 2):
            left = mid_index - i
            right = mid_index + i

            if self.sync_front_up:
                if s[left - 1] <= self.sync_level <= s[left]:
                    return left - 1
                if s[right] <= self.sync_level <= s[right + 1]:
                    return right
            else:
                if s[left - 1] >= self.sync_level >= s[left]:
                    return left - 1
                if s[right] >= self.sync_level >= s[right + 1]:
                    return right

        return 0

    @staticmethod
    def _get_local_min(f):
        sign = (MyList(f) - f[1:]) <= 0
        i1 = iter(sign)
        i2 = iter(sign)
        next(i2)

        for i, (p, n) in enumerate(zip(i1, i2)):
            if not p and n:
                yield i

    @staticmethod
    def _get_period(f):
        f = MyList(f)

        delta = MyList([sq(f - f[i:]) / (len(f[i:])) for i in range(len(f) - 100)])

        _periods = MyList(SignalProcessor._get_local_min(delta))[:-1]

        mid_value = sum(delta) / len(delta)

        periods = [p for p in _periods if delta[p] < mid_value]

        mid = MyList(periods[1:]) - periods

        if 0 == len(mid):
            return 0

        return sum(mid) / len(mid)

