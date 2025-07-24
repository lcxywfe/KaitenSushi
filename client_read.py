import asyncio
import ucp
import numpy as np

from utils import *

length = 100 * 1024 * 1024

async def main():
    ep = await ucp.create_endpoint("127.0.0.1", 13337)
    ch = ClientHeader("read", length)
    await ep.send(ch.buffer)

    idx = 0
    while True:
        key = "key{}".format(idx)
        fh = FeatureHeader(key)
        await ep.send(fh.buffer)

        buf = np.arange(length, dtype=np.uint8)
        logging.info("[Reader] receiving key: {}".format(key))
        await ep.recv(buf)
        logging.info("[Reader] received key: {}".format(key))
        idx += 1
        await asyncio.sleep(1)

        if idx == 10:
            fh = FeatureHeader("close")
            await ep.send(fh.buffer)
            break

    await ep.close()


if __name__ == "__main__":
    init_logging()
    ucp.init()
    asyncio.run(main())