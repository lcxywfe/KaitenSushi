cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(kaitensushi)

set(UCX_DIR "/opt/ucx/lib/cmake/ucx")
find_package(UCX REQUIRED)
message(STATUS "UCX_INCLUDE_DIRS = ${UCX_INCLUDE_DIRS}")
message(STATUS "UCX_LIBRARIES = ${UCX_LIBRARIES}")

include_directories(${UCX_INCLUDE_DIRS})
link_directories(${UCX_LIBRARIES})

add_executable(write test/write.cpp)

target_include_directories(write PUBLIC include)
target_link_libraries(write ucp)