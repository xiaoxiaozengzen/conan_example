cmake_minimum_required(VERSION 3.23)
project(MD5Encrypter)

if(ENABLE_CMAKE_VERBOSE)
    set(CMAKE_VERBOSE_MAKEFILE ON)
endif()

add_definitions("-std=c++11")

if(DEFINED CMAKE_BUILD_TYPE)
    message(STATUS "CMAKE_BUILD_TYPE is defined: ${CMAKE_BUILD_TYPE}")
else()
    message(STATUS "CMAKE_BUILD_TYPE is not defined")
endif()

message(STATUS "CMAKE_C_FLAGS: ${CMAKE_C_FLAGS}")
message(STATUS "CMAKE_CXX_FLAGS: ${CMAKE_CXX_FLAGS}")

find_package(Nihao REQUIRED)
find_package(World REQUIRED)
find_package(HEllo REQUIRED)

message(STATUS "Nihao_LIBRARIES: ${Nihao_LIBRARIES}")
message(STATUS "Nihao_INCLUDE_DIRS: ${Nihao_INCLUDE_DIRS}")
message(STATUS "World_LIBRARIES: ${World_LIBRARIES}")
message(STATUS "World_INCLUDE_DIRS: ${World_INCLUDE_DIRS}")
message(STATUS "HEllo_LIBRARIES: ${HEllo_LIBRARIES}")
message(STATUS "HEllo_INCLUDE_DIRS: ${HEllo_INCLUDE_DIRS}")

add_executable(test_exe test.cpp)
target_link_libraries(test_exe ${Nihao_LIBRARIES} ${World_LIBRARIES} HEllo::hello)
target_include_directories(test_exe PUBLIC ${Nihao_INCLUDE_DIRS} ${World_INCLUDE_DIRS} ${HEllo_INCLUDE_DIRS})

if(BUILD_MAIN)
target_compile_definitions(test_exe PUBLIC HELLO_MAIN)
endif()

if(DEFINED BUILD_TESTING)
    message(STATUS "BUILD_TESTING is defined: ${BUILD_TESTING}")
else()
    message(STATUS "BUILD_TESTING is not defined")
endif()
