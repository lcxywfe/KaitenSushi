import kaitensushi as kss
import asyncio

kss.init(log_level='debug')
asyncio.run(kss.start_server(13337))
