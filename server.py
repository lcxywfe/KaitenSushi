import asyncio
import ucp
import numpy as np
import logging

from utils import *

feature_dict = dict()
finish_dict = dict()

lock = asyncio.Lock()

async def send_when_ready(ep, key, length):
    while key not in finish_dict:
        await asyncio.sleep(0.01)
    async with lock:
        buf = feature_dict[key]
    assert len(buf) == KEY_BYTES + length
    logging.info("[Server] Sending to client: {}, key: {}".format(ep.uid, key))
    await ep.send(buf)
    logging.info("[Server] Sent to client: {}, key: {}".format(ep.uid, key))

async def handler(ep):

    ch = ClientHeader()
    await ep.recv(ch.buffer)
    logging.info("[Server] Connected client uid: {}, mode: {}, length {}".format(ep.uid, ch.mode(), ch.length()))

    tasks = []

    while True:
        fh = FeatureHeader()
        await ep.recv(fh.buffer)
        if fh.key() == "close":
                break
        key = fh.key()

        if ch.mode() == "write":
            async with lock:
                assert key not in feature_dict
                buf = np.empty(KEY_BYTES + ch.length(), dtype=np.uint8)
                buf[:KEY_BYTES] = np.frombuffer(key.encode().ljust(KEY_BYTES, b' '), dtype=np.uint8)
                feature_dict[key] = buf

            logging.info("[Server] Receiving from client: {}, key: {}".format(ep.uid, key))
            await ep.recv(feature_dict[fh.key()][KEY_BYTES:])
            logging.info("[Server] Received from client: {}, key: {}".format(ep.uid, key))

            async with lock:
                finish_dict[key] = True

        elif ch.mode() == "read":
            task = asyncio.create_task(send_when_ready(ep, key, ch.length()))
            tasks.append(task)

        else:
            logging.info("[Server] Unknown client mode: {}".format(ch.mode()))

    await asyncio.gather(*tasks)
    await ep.close()

async def main():
    listener = ucp.create_listener(handler, port=13337)
    logging.info("[Server] Listening on port {}".format(listener.port))
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    init_logging()
    ucp.init()
    asyncio.run(main())