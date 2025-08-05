# Kaiten Sushi

## requirements
#### python
```conda install -c conda-forge -c rapidsai ucx-py```

#### c++
```
git clone https://github.com/openucx/ucx.git
cd ucx && git checkout v1.8.1
./autogen.sh
./contrib/configure-release --prefix=/usr/local --enable-mt
make -j$(nproc)
sudo make install

git clone https://github.com/rapidsai/ucxx.git
cd ucxx/cpp
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_TESTS=OFF
make -j$(nproc)
sudo make install
```


## install
#### python
 ```pip install .```

#### c++
```
cd src
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```


## example
#### server
```
import kaitensushi as kss
import asyncio
kss.init()
asyncio.run(kss.start_server(13337))
```

#### writer
```
#include <kaitensushi/writer.h>
using namespace kss;
int main() {
    kss::Writer<true> writer{"10.10.10.72", 13337};
    std::string s = "0123456789";
    writer.write("key_num", static_cast<const void*>(s.data()), s.size());
    writer.wait();
    return 0;
}
```

#### reader
```
import kaitensushi as kss
kss.init()
reader = kss.Reader("127.0.0.1", 13337)
bufs = reader.read(["key2", "key1", "key0"])
reader.close()
```
