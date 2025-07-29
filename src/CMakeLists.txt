cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(kaitensushi)


find_package(UCX REQUIRED)
find_package(UCXX REQUIRED)

set(INSTALL_INCLUDE_DIR include)
set(INSTALL_LIB_DIR lib)

add_library(kaitensushi SHARED writer.cpp)

install(DIRECTORY include/kaitensushi/
        DESTINATION ${INSTALL_INCLUDE_DIR}/kaitensushi
        FILES_MATCHING PATTERN "*.h")

install(TARGETS kaitensushi LIBRARY DESTINATION ${INSTALL_LIB_DIR})

target_include_directories(kaitensushi PUBLIC include)
target_link_libraries(kaitensushi PUBLIC ucxx::ucxx)
