import kaitensushi as kss
import asyncio

kss.init()
asyncio.run(kss.start_server(13337))
