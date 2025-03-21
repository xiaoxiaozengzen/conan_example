cmake_minimum_required(VERSION 3.1)
project(world CXX)

find_package(HEllo REQUIRED)

add_library(world SHARED src/world.cpp)
target_include_directories(
    world PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${hello_INCLUDE_DIRS}
)
target_link_libraries(world PUBLIC HEllo::hello)

