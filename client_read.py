import asyncio
import queue
import threading
import time
import ucp
import numpy as np

from utils import *

length = 100 * 1024 * 1024

key_queue = queue.Queue()
buf_map = dict()
buf_con = threading.Condition()

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
        buf = np.empty(length, dtype=np.uint8)
        await ep.recv(buf)
        logging.info("[Reader] received key: {}".format(key))
        with buf_con:
            buf_map[key] = buf
            buf_con.notify_all()

    await ep.close()

def async_reader():
    asyncio.run(read())

def wait_for(key):
    with buf_con:
        while key not in buf_map:
            buf_con.wait()
        return buf_map.pop(key)

if __name__ == "__main__":
    init_logging()
    ucp.init()

    t_reader = threading.Thread(target=async_reader)
    t_reader.start()
    logging.info("Async reader threading start")

    time.sleep(1)

    key_queue.put("key2")
    key_queue.put("key0")
    key_queue.put("key1")

    buf = wait_for("key0")
    logging.info("Got {}".format("key0"))
    time.sleep(1)

    buf = wait_for("key1")
    logging.info("Got {}".format("key1"))
    time.sleep(1)

    buf = wait_for("key2")
    logging.info("Got {}".format("key2"))
    time.sleep(1)


    key_queue.put("close")

    t_reader.join()
    logging.info("Reader finished")