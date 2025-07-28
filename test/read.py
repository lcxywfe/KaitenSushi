import kaitensushi as kss

kss.init()

reader = kss.Reader("127.0.0.1", 13337)

reader.read(["key0", "key1", "key2"])

reader.close()
