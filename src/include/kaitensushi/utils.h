#pragma once

namespace kss {

template <class MutexType>
class ConditionalLock {
public:
    ConditionalLock(MutexType* mtx) : mtx_(mtx) {
        if (mtx_) {
            mtx_->lock();
        }
    }

    ~ConditionalLock() {
        if (mtx_) {
            mtx_->unlock();
        }
    }

private:
    MutexType* mtx_;
};

}