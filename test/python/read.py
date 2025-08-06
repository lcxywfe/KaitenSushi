import kaitensushi as kss

kss.init()

reader = kss.Reader("127.0.0.1", 13337)

print(reader.read("key0"))
print(reader.read(["key2", "key1"]))

reader.close()
