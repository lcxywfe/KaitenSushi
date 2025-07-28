import asyncio
import queue
import threading
import time
import ucp
import numpy as np

from utils import *

length = 100 * 1024 * 1024
batch = 3

key_queue = queue.Queue()
buf_map = dict()
buf_con = threading.Condition()

async def read():
    ep = await ucp.create_endpoint("127.0.0.1", 13337)
    ch = ClientHeader("read")
    await ep.send(ch.buffer)
    while True:
        keys = key_queue.get()
        if len(keys) == 1 and keys[0] == "close":
            fh = FeatureHeader("close")
            await ep.send(fh.buffer)
            break

        fhs = []
        bufs = []
        for key in keys:
            fhs.append(FeatureHeader(key, length))
            bufs.append(np.empty(KEY_BYTES + length, dtype=np.uint8))

        logging.info("[Reader] receiving keys: {}".format(keys))
        n = len(keys)
        sends = [ep.send(fhs[i].buffer) for i in range(n)]
        recvs = [ep.recv(bufs[i]) for i in range(n)]
        await asyncio.gather(*sends, *recvs)
        logging.info("[Reader] received keys: {}".format(keys))

        for buf in bufs:
            with buf_con:
                key = buf[:KEY_BYTES].tobytes().decode().rstrip()
                logging.info("Got {}".format(key))
                buf_map[key] = buf[KEY_BYTES:]
                buf_con.notify_all()

    await ep.close()

def async_reader():
    asyncio.run(read())

def wait_for(keys):
    bufs = dict()
    for key in keys:
        with buf_con:
            while key not in buf_map:
                buf_con.wait()
            bufs[key] = buf_map.pop(key)
    return bufs

if __name__ == "__main__":
    init_logging()
    ucp.init()

    t_reader = threading.Thread(target=async_reader)
    t_reader.start()
    logging.info("Async reader threading start")

    time.sleep(1)

    key_queue.put(["key2", "key0", "key1"])

    bufs = wait_for(["key0", "key1", "key2"])
    logging.info(bufs)

    key_queue.put(["close"])

    t_reader.join()
    logging.info("Reader finished")