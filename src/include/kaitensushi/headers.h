#pragma once
#include <cassert>
#include <cstring>
#include <string>

namespace kss {

const static size_t MODE_BYTES = 8;
const static size_t KEY_BYTES = 64;
const static size_t LENGTH_BYTES = 8;

class Header {
public:
    Header(size_t length) : buffer_{std::string(length, ' ')} {}
    virtual ~Header() = default;
    std::string& buffer() { return buffer_; }

protected:
    std::string buffer_;
};

class ClientHeader : public Header {
public:
    ClientHeader(const std::string& mode) : Header{MODE_BYTES} {
        assert(mode.size() <= buffer_.size());
        std::memcpy(&buffer_[0], mode.data(), mode.size());
    }
};

class FeatureHeader : public Header {
public:
    FeatureHeader(const std::string& key, uint64_t length = 0)
                : Header{KEY_BYTES + LENGTH_BYTES} {
        std::memcpy(&buffer_[0], key.data(), key.size());
        std::memcpy(&buffer_[0] + KEY_BYTES, &length, sizeof(length));
    }
};

}