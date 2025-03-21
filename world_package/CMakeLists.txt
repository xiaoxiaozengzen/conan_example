cmake_minimum_required(VERSION 3.1)
project(world CXX)

# find_package(hello REQUIRED)

add_library(world src/world.cpp)
target_include_directories(
    world PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_INCLUDE_PATH}
)

