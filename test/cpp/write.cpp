#include <iostream>
#include <chrono>
#include <thread>

#include <kaitensushi/writer.h>

using namespace kss;

int main() {
    kss::Writer writer{"10.10.10.72", 13337};
    std::string s(10, '\0');
    for (int i = 0; i < s.size(); ++i) {
        s[i] = static_cast<unsigned char>(i);
    }
    writer.write("key_num", static_cast<const void*>(s.data()), s.size());
    writer.wait();
    return 0;
}