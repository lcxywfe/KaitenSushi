import asyncio
import ucp
import numpy as np
import logging

from .utils import *

feature_dict = dict()
finish_dict = dict()

feature_lock = asyncio.Lock()
finish_cond = asyncio.Condition()

async def recv(ep, key, length):
    buf = np.empty(KEY_BYTES + length, dtype=np.uint8)
    buf[:KEY_BYTES] = np.frombuffer(key.encode().ljust(KEY_BYTES, b' '), dtype=np.uint8)
    async with feature_lock:
        feature_dict[key] = buf

    logging.debug("[Kss Server] Receiving from client: {}, key: {}".format(ep.uid, key))
    await ep.recv(feature_dict[key][KEY_BYTES:])
    logging.debug("[Kss Server] Received from client: {}, key: {}".format(ep.uid, key))

    async with finish_cond:
        finish_dict[key] = True
        finish_cond.notify_all()

async def send_when_ready(ep, key, length):
    async with finish_cond:
        await finish_cond.wait_for(lambda: key in finish_dict)

    async with feature_lock:
        buf = feature_dict[key]
    assert len(buf) == KEY_BYTES + length, (len(buf), KEY_BYTES, length)
    logging.debug("[Kss Server] Sending to client: {}, key: {}".format(ep.uid, key))
    await ep.send(buf)
    logging.debug("[Kss Server] Sent to client: {}, key: {}".format(ep.uid, key))

async def server(ep):
    ch = ClientHeader()
    await ep.recv(ch.buffer)
    logging.info("[Kss Server] Connected client uid: {}, mode: {}".format(ep.uid, ch.mode()))

    tasks = []

    while True:
        fh = FeatureHeader()
        await ep.recv(fh.buffer)
        if fh.key() == "close":
            logging.info("[Kss Server] connection closed uid: {}".format(ep.uid))
            break
        key = fh.key()
        logging.debug("[Kss Server] received header key: {}".format(key))

        if ch.mode() == "write":
            await recv(ep, key, fh.length())

        elif ch.mode() == "read":
            task = asyncio.create_task(send_when_ready(ep, key, fh.length()))
            # tasks.append(task)

        else:
            logging.error("[Kss Server] Unknown client mode: {}".format(ch.mode()))

    await asyncio.gather(*tasks)
    await ep.close()

async def start_server(port):
    listener = ucp.create_listener(server, port=port)
    logging.info("[Kss Server] Listening on port {}".format(listener.port))
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    init_logging()
    ucp.init()
    asyncio.run(start_server(13337))
