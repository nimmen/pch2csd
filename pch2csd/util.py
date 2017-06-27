import logging
from struct import unpack
from typing import List

from bitarray import bitarray


class AttrEqMixin:
    def attrs_equal(self, other):
        if type(self) != type(other):
            return False
        attrs_self = self.__dict__
        attrs_other = other.__dict__
        if set(attrs_self.keys()) != set(attrs_other.keys()):
            return False
        for key in attrs_self.keys():
            if attrs_self[key] != attrs_other[key]:
                return False
        return True


class ReprStrMixin:
    def __repr__(self):
        return f"{type(self).__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items()])})"

    def __str__(self):
        return self.__repr__()


class LogMixin:
    __logger = None
    __log_name = None

    def logger_set_name(self, name: str):
        self.__log_name = name
        self.__logger = None

    @property
    def log(self) -> logging.Logger:
        if self.__logger is None:
            self.__logger = logging.getLogger(self.__log_name)
        return self.__logger


class BitArrayStream:
    def __init__(self, bits: bitarray):
        self.pos = 0
        self.bits = bits

    def _read_int(self, int_len: int):
        b = self.bits[self.pos:self.pos + int_len].tobytes()
        if 0 < int_len <= 8:
            num = unpack('>B', b)[0]
            num = num >> 8 - int_len
        elif 8 < int_len <= 16:
            num = unpack('>H', b)[0]
            num = num >> 16 - int_len
        else:
            raise NotImplementedError
        self.pos += int_len
        return num

    def read_ints(self, bit_chunks: List[int]):
        if sum(bit_chunks) + self.pos > len(self.bits):
            raise ValueError("Don't have enough data to read")
        return [self._read_int(i) for i in bit_chunks]


def preprocess_csd_code(code: str) -> str:
    lines = code.splitlines()
    if lines[-1] != '':
        lines += ''
    return '\n'.join(lines)