from typing import List


class Signal:
    def __init__(self, data: List[int], hz: float):
        self.data = data
        self.hz = hz
        self.sync_index = None

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




