import asyncio
import ucp
import numpy as np
import logging

from utils import *

feature_dict = dict()

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

        if ch.mode() == "write":
            async with lock:
                feature_dict[fh.key()] = np.empty(ch.length(), dtype=np.uint8)
            logging.info("[Server] Receiving from client: {}, key: {}".format(ep.uid, fh.key()))
            await ep.recv(feature_dict[fh.key()])
            logging.info("[Server] Received from client: {}, key: {}".format(ep.uid, fh.key()))

        elif ch.mode() == "read":
            async with lock:
                buf = feature_dict[fh.key()]
            assert len(buf) == ch.length()
            logging.info("[Server] Sending to client: {}, key: {}".format(ep.uid, fh.key()))
            await ep.send(buf)
            logging.info("[Server] Sent to client: {}, key: {}".format(ep.uid, fh.key()))
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