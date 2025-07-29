import kaitensushi as kss

kss.init()

reader = kss.Reader("127.0.0.1", 13337)

bufs = reader.read(["key2", "key1", "key0"])

reader.close()

for key,  buf in bufs.items():
    print(key, buf.mean())