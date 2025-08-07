import kaitensushi as kss

length = 100 * 1024 * 1024

kss.init("debug")

reader = kss.Reader("127.0.0.1", 13337)

print(reader.read("key0", length))
print(reader.read(["key2", "key1"], [length, length]))

reader.close()
