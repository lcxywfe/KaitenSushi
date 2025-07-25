import asyncio
import queue
import threading
import time
import ucp
import numpy as np

from utils import *

length = 100 * 1024 * 1024

key_queue = queue.Queue()
buf_queue = queue.Queue()

async def read():
    ep = await ucp.create_endpoint("127.0.0.1", 13337)
    ch = ClientHeader("read", length)
    await ep.send(ch.buffer)
    while True:
        key = key_queue.get()
        if key == "close":
            fh = FeatureHeader("close")
            await ep.send(fh.buffer)
            break

        fh = FeatureHeader(key)
        await ep.send(fh.buffer)

        logging.info("[Reader] receiving key: {}".format(key))
        buf = np.arange(length, dtype=np.uint8)
        await ep.recv(buf)
        logging.info("[Reader] received key: {}".format(key))
        buf_queue.put(buf)

    await ep.close()

def async_reader():
    asyncio.run(read())

if __name__ == "__main__":
    init_logging()
    ucp.init()

    t_reader = threading.Thread(target=async_reader)
    t_reader.start()
    logging.info("Async reader threading start")

    time.sleep(1)

    key = "key1"
    key_queue.put(key)
    buf = buf_queue.get()
    logging.info("Got {}".format(key))

    time.sleep(1)

    key = "key0"
    key_queue.put(key)
    buf = buf_queue.get()
    logging.info("Got {}".format(key))

    key_queue.put("close")

    t_reader.join()
    logging.info("Reader finished")