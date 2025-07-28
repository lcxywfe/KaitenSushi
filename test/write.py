import asyncio
import logging
import ucp
import numpy as np

import kaitensushi as kss

length = 100 * 1024 * 1024

async def main():
    ep = await ucp.create_endpoint("127.0.0.1", 13337)
    ch = kss.ClientHeader("write")
    await ep.send(ch.buffer)

    idx = 0
    while True:
        key = "key{}".format(idx)
        fh = kss.FeatureHeader(key, length)
        await ep.send(fh.buffer)

        buf = np.arange(length, dtype=np.uint8)
        logging.info("[Writer] Sending key: {}".format(key))
        await ep.send(buf)
        logging.info("[Writer] Sent key: {}".format(key))
        idx += 1
        await asyncio.sleep(1)

        if idx == 3:
            fh = kss.FeatureHeader("close")
            await ep.send(fh.buffer)
            break

    await ep.close()

if __name__ == "__main__":
    kss.init()
    asyncio.run(main())