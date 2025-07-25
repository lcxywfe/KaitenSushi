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
    def __init__(self, mode = None, length = None):
        self.buffer = bytearray(MODE_BYTES + LENGTH_BYTES)
        if mode is not None:
            self.buffer[:8] = mode.encode().ljust(8, b' ')
        if length is not None:
            self.buffer[8:16] = struct.pack('Q', length)

    def mode(self):
        return self.buffer[:8].decode().rstrip()

    def length(self):
        return struct.unpack("Q", self.buffer[8:])[0]

class FeatureHeader:
    def __init__(self, key = None):
        self.buffer = bytearray(KEY_BYTES)
        if key is not None:
            self.buffer = key.encode().ljust(64, b' ')

    def key(self):
        return self.buffer.decode().rstrip()
