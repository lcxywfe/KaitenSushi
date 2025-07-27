import asyncio
import ucp
import numpy as np

from utils import *

length = 100 * 1024 * 1024

async def main():
    ep = await ucp.create_endpoint("127.0.0.1", 13337)
    ch = ClientHeader("write")
    await ep.send(ch.buffer)

    idx = 0
    while True:
        key = "key{}".format(idx)
        fh = FeatureHeader(key, length)
        await ep.send(fh.buffer)

        buf = np.arange(length, dtype=np.uint8)
        logging.info("[Writer] Sending key: {}".format(key))
        await ep.send(buf)
        logging.info("[Writer] Sent key: {}".format(key))
        idx += 1
        await asyncio.sleep(1)

        if idx == 3:
            fh = FeatureHeader("close")
            await ep.send(fh.buffer)
            break

    await ep.close()

if __name__ == "__main__":
    init_logging()
    ucp.init()
    asyncio.run(main())