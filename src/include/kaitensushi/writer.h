#pragma once

#include <mutex>
#include <unordered_map>
#include <ucxx/api.h>

namespace kss {

class Client {
public:
    Client(const std::string& addr, int port);
    virtual ~Client();

protected:
    void exchange_peer_info();

protected:
    std::shared_ptr<ucxx::Context> context_;
    std::shared_ptr<ucxx::Worker> worker_;
    std::shared_ptr<ucxx::Endpoint> ep_;
    std::unordered_map<std::string, uint64_t> tags_;
};

class Writer : public Client {
public:
    Writer(const std::string& addr, int port);

    void write(const std::string& key, const void* ptr, uint64_t length);

private:
    std::mutex mtx_;
};

}