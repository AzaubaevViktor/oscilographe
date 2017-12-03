from typing import List

import serial.tools.list_ports
import time

import sys


def limit(value, down, up):
    if value < down:
        return down
    if value > up:
        return up
    return value


class Arduino:
    def __init__(self):
        ports = serial.tools.list_ports.comports()
        print(ports)

        self.port = None
        
        for port in ports:
            try:
                self._connect(port)
            except OSError:
                print("Fuck")

        if self.port is None:
            raise Exception("Not found Arduino")

        time.sleep(1)

    def _connect(self, port):
        print("Conect to port {}".format(port))
            
        self.connection = serial.Serial(port.device, baudrate=256000)      

        self.port = port

    def _write(self, data):
        return self.connection.write(bytes(data))

    def _read(self, count=1) -> List[int] or int:
        data = [int(x) for x in self.connection.read(count)]
        if 1 == count:
            return data[0]
        else:
            return data

    def _check_start(self, data) -> List[int]:
        return data == [1, 15, 1, 15, 0, 15]

    def read_data(self):
        d = self._read(6)

        while not self._check_start(d):
            d = d[1:]
            d.append(self._read())

        data = self._read(1024)
        tm = self._read(4)
        micros = tm[0] + tm[1] * 256 + tm[2] * 256 * 256 + tm[3] * 256 * 256 * 256
        print(micros)

        return data, micros / 1024

    def set_divider(self, value):
        value = limit(int(value), 0, 7)
        print("Set divider to {}".format(value))
        self._write([1, value])


if __name__ == "__main__":
    a = Arduino()
    t1 = time.time()
    for x in range(100):
        d = a.read_data()
        print(sum(d) / len(d))

    t2 = time.time()
    print((100 * 1024) / (t2 -t1))



