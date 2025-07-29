cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(kaitensushi_test)

find_package(UCX REQUIRED)
find_package(UCXX REQUIRED)

add_executable(test write.cpp)

target_link_libraries(test PRIVATE kaitensushi)
target_link_libraries(test PUBLIC ucxx::ucxx)


