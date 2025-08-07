import asyncio
import queue
import threading
import time
import ucp
import numpy as np

from .utils import *

key_queue = queue.Queue()
len_queue = queue.Queue()
buf_map = dict()
buf_con = threading.Condition()

async def start_reader(addr, port):
    ep = await ucp.create_endpoint(addr, port)
    ch = ClientHeader("read")
    await ep.send(ch.buffer)
    logging.info("[Kss Reader] connected")
    while True:
        keys = key_queue.get()
        if len(keys) == 1 and keys[0] == "close":
            fh = FeatureHeader("close")
            await ep.send(fh.buffer)
            break

        lens = len_queue.get()
        fhs = []
        bufs = []
        for key, length in zip(keys, lens):
            fhs.append(FeatureHeader(key, length))
            bufs.append(np.empty(KEY_BYTES + length, dtype=np.uint8))

        logging.debug("[Kss Reader] receiving keys: {}".format(keys))
        n = len(keys)
        sends = [ep.send(fhs[i].buffer) for i in range(n)]
        recvs = [ep.recv(bufs[i]) for i in range(n)]
        await asyncio.gather(*sends, *recvs)
        logging.debug("[Kss Reader] received keys: {}".format(keys))

        for buf in bufs:
            with buf_con:
                key = buf[:KEY_BYTES].tobytes().decode().rstrip()
                logging.debug("[Kss Reader] Got {}".format(key))
                buf_map[key] = buf[KEY_BYTES:]  # TODO opt zero copy
                buf_con.notify_all()

    await ep.close()

def run_reader(addr, port):
    asyncio.run(start_reader(addr, port))

class Reader:
    def __init__(self, addr, port):
        self._reader = threading.Thread(target=run_reader, args=(addr, port))
        self._reader.start()

    def __del__(self):
        self.close()

    def read(self, keys, lens):
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
            lens = [lens]

        key_queue.put(keys)
        len_queue.put(lens)

        bufs = dict()
        for key in keys:
            with buf_con:
                while key not in buf_map:
                    buf_con.wait()
                bufs[key] = buf_map.pop(key)

        if len(keys) == 1:
            return bufs[keys[0]]
        return bufs

    def close(self):
        if self._reader is not None:
            logging.info("[Kss Reader] close")
            key_queue.put(["close"])
            self._reader.join()
            self._reader = None