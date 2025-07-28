#pragma once

#include <cstring>
#include <string>

namespace ifq {
namespace kss {

const static size_t MODE_BYTES = 8;
const static size_t KEY_BYTES = 64;
const static size_t LENGTH_BYTES = 8;

class ClientHeader {
public:
    ClientHeader(const std::string& mode) {
        buffer = mode + std::string(MODE_BYTES - mode.size(), ' ');
    }

private:
    std::string buffer;
};

class FeatureHeader {
public:
    FeatureHeader(const std::string& key, uint64_t length) {
        std::string key_str = key + std::string(KEY_BYTES - key.size(), ' ');
        std::string len_str = std::string(LENGTH_BYTES, ' ');
        std::memcpy(&len_str[0], &length, sizeof(LENGTH_BYTES));
        buffer = key_str + len_str;
    }

private:
    std::string buffer;

};


}
}