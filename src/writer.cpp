#include <iostream>
#include <ucxx/request_helper.h>

#include <kaitensushi/headers.h>
#include <kaitensushi/writer.h>
#include <kaitensushi/utils.h>

using namespace kss;

template <bool thread_safe>
Client<thread_safe>::Client(const std::string& addr, int port) :
            mtx_{},
            requests_{} {
    context_ = ucxx::createContext({}, ucxx::Context::defaultFeatureFlags);
    worker_ = context_->createWorker();
    ep_ = worker_->createEndpointFromHostname(addr, port, true);
}

template <bool thread_safe>
Client<thread_safe>::~Client() {
    if (ep_) {
        FeatureHeader fh{"close"};
        auto request = ep_->tagSend(fh.buffer().data(), fh.buffer().size(), ucxx::Tag(tags_.at("msg_send")));
        ucxx::waitSingleRequest(worker_, request);

        ep_->closeBlocking();
    }
}

template <bool thread_safe>
void Client<thread_safe>::exchange_peer_info() {
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

template <bool thread_safe>
void Client<thread_safe>::wait() {
    if (thread_safe) {
        mtx_.lock();
    }
    ucxx::waitRequests(worker_, requests_);
    requests_.clear();
    if (thread_safe) {
        mtx_.unlock();
    }
}


template <bool thread_safe>
Writer<thread_safe>::Writer(const std::string& addr, int port)
        : Client<thread_safe>{addr, port} {
    this->exchange_peer_info();
    ClientHeader ch{"write"};
    auto request = this->ep_->tagSend(ch.buffer().data(), ch.buffer().size(), ucxx::Tag(this->tags_.at("msg_send")));
    ucxx::waitSingleRequest(this->worker_, request);
}

template <bool thread_safe>
void Writer<thread_safe>::write(const std::string& key, const void* ptr, uint64_t length) {
    if (thread_safe) {
        this->mtx_.lock();
    }
    {
        FeatureHeader fh{key, length};
        auto request = this->ep_->tagSend(fh.buffer().data(), fh.buffer().size(), ucxx::Tag(this->tags_.at("msg_send")));
        this->requests_.push_back(request);
    }

    {
        auto request = this->ep_->tagSend(const_cast<void*>(ptr), length, ucxx::Tag(this->tags_.at("msg_send")));
        this->requests_.push_back(request);
    }
    if (thread_safe) {
        this->mtx_.unlock();
    }
}

template class Client<true>;
template class Client<false>;
template class Writer<true>;
template class Writer<false>;
