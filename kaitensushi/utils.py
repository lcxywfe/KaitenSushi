import logging
import struct
import ucp


MODE_BYTES = 8
LENGTH_BYTES = 8
KEY_BYTES = 64

def init_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(levelname).1s%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d] %(message)s',
        datefmt='%m%d %H:%M:%S',
    )

def init(log_level = "info"):
    '''
    Needs to be called within the actural process where it will be used.
    '''
    assert log_level in ("info", "debug"), log_level
    if log_level == "info":
        l = logging.INFO
    elif log_level == "debug":
        l = logging.DEBUG
    init_logging(l)
    ucp.init()

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
