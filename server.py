import asyncio
import ucp
import numpy as np
import logging

from utils import *

feature_dict = dict()
finish_dict = dict()

lock = asyncio.Lock()

async def handler(ep):

    ch = ClientHeader()
    await ep.recv(ch.buffer)
    logging.info("[Server] Connected client uid: {}, mode: {}, length {}".format(ep.uid, ch.mode(), ch.length()))

    while True:
        fh = FeatureHeader()
        await ep.recv(fh.buffer)
        if fh.key() == "close":
                break
        key = fh.key()

        if ch.mode() == "write":
            async with lock:
                assert key not in feature_dict
                feature_dict[key] = np.empty(ch.length(), dtype=np.uint8)

            logging.info("[Server] Receiving from client: {}, key: {}".format(ep.uid, key))
            await ep.recv(feature_dict[fh.key()])
            logging.info("[Server] Received from client: {}, key: {}".format(ep.uid, key))

            async with lock:
                finish_dict[key] = True

        elif ch.mode() == "read":
            while True:
                if key in finish_dict:
                    break
                logging.info("[Server] Waiting for key: {}".format(key))
                await asyncio.sleep(0.01)

            async with lock:
                buf = feature_dict[key]
            assert len(buf) == ch.length()
            logging.info("[Server] Sending to client: {}, key: {}".format(ep.uid, key))
            await ep.send(buf)
            logging.info("[Server] Sent to client: {}, key: {}".format(ep.uid, key))
        else:
            logging.info("[Server] Unknown client mode: {}".format(ch.mode()))

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