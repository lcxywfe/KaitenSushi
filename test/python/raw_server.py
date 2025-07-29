import ucp
import asyncio

async def raw_handler(ep):
    print("Accepted connection")
    msg = bytearray(1024)
    nbytes = await ep.recv(msg)
    print("Received:", msg[:nbytes])
    await ep.close()

async def main():
    ucp.init()
    listener = ucp.create_listener(raw_handler, port=13337)
    print("Listening on port 13337")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())