import logging
import struct

MODE_BYTES = 8
LENGTH_BYTES = 8
KEY_BYTES = 64

def init_logging(level=logging.INFO):
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname).1s%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d] %(message)s',
        datefmt='%m%d %H:%M:%S',
    )

class ClientHeader:
    def __init__(self, mode = None):
        self.buffer = bytearray(MODE_BYTES)
        if mode is not None:
            self.buffer[:MODE_BYTES] = mode.encode().ljust(MODE_BYTES, b' ')

    def mode(self):
        return self.buffer[:MODE_BYTES].decode().rstrip()

class FeatureHeader:
    def __init__(self, key = None, length = None):
        self.buffer = bytearray(KEY_BYTES + LENGTH_BYTES)
        if key is not None:
            self.buffer[:KEY_BYTES] = key.encode().ljust(KEY_BYTES, b' ')
        if length is not None:
            self.buffer[KEY_BYTES:] = struct.pack('Q', length)

    def key(self):
        return self.buffer[:KEY_BYTES].decode().rstrip()

    def length(self):
        return struct.unpack("Q", self.buffer[KEY_BYTES:])[0]
