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
```


## install
* ```pip install .```