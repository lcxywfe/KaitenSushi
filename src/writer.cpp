#include <iostream>
#include <ucxx/request_helper.h>

#include <kaitensushi/headers.h>
#include <kaitensushi/writer.h>
#include <kaitensushi/utils.h>

using namespace kss;

Client::Client(const std::string& addr, int port, bool thread_safe) :
            mtx_{thread_safe ? std::make_unique<std::mutex>() : nullptr},
            requests_{} {
    context_ = ucxx::createContext({}, ucxx::Context::defaultFeatureFlags);
    worker_ = context_->createWorker();
    ep_ = worker_->createEndpointFromHostname(addr, port, true);
}

Client::~Client() {
    if (ep_) {
        FeatureHeader fh{"close"};
        auto request = ep_->tagSend(fh.buffer().data(), fh.buffer().size(), ucxx::Tag(tags_.at("msg_send")));
        ucxx::waitSingleRequest(worker_, request);

        ep_->closeBlocking();
    }
}

void Client::exchange_peer_info() {
    std::string buf0(24, ' ');
    auto r0 = ep_->streamRecv(&buf0[0], 24, false);
    ucxx::waitSingleRequest(worker_, r0);
    uint64_t msg_tag = *(reinterpret_cast<uint64_t*>(&buf0[0]));
    std::cout << "msg_tag: " << msg_tag << std::endl;
    tags_["msg_send"] = msg_tag;

    // TODO send same tag now
    auto r1 = ep_->streamSend(&buf0[0], 24, false);
    ucxx::waitSingleRequest(worker_, r1);
}

void Client::wait() {
    ConditionalLock<std::mutex> lock{mtx_.get()};
    ucxx::waitRequests(worker_, requests_);
    requests_.clear();
}


Writer::Writer(const std::string& addr, int port, bool thread_safe)
        : Client{addr, port, thread_safe} {
    exchange_peer_info();
    ClientHeader ch{"write"};
    auto request = ep_->tagSend(ch.buffer().data(), ch.buffer().size(), ucxx::Tag(tags_.at("msg_send")));
    ucxx::waitSingleRequest(worker_, request);
}


void Writer::write(const std::string& key, const void* ptr, uint64_t length) {
    ConditionalLock<std::mutex> lock{mtx_.get()};
    {
        FeatureHeader fh{key, length};
        auto request = ep_->tagSend(fh.buffer().data(), fh.buffer().size(), ucxx::Tag(tags_.at("msg_send")));
        requests_.push_back(request);
    }

    {
        auto request = ep_->tagSend(const_cast<void*>(ptr), length, ucxx::Tag(tags_.at("msg_send")));
        requests_.push_back(request);
    }
}