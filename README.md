# Kaiten Sushi

## requirements
#### python
```conda install -c conda-forge -c rapidsai ucx-py```

#### c++
```
sudo mkdir -p /opt/ucx
git clone https://github.com/openucx/ucx.git
cd ucx && git checkout v1.8.1
./autogen.sh
./contrib/configure-release --prefix=/opt/ucx --enable-mt
make -j$(nproc)
sudo make install

sudo mkdir -p /opt/ucxx
git clone https://github.com/rapidsai/ucxx.git
cd ucxx/cpp
mkdir build && build
cmake .. -DCMAKE_INSTALL_PREFIX=/opt/ucxx -DCMAKE_PREFIX_PATH=/opt/ucx -DBUILD_TESTS=OFF
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