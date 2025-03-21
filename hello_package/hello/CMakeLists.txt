cmake_minimum_required(VERSION 3.1)
project(hello CXX)

find_package(Protobuf REQUIRED)
message(STATUS "Protobuf_FOUND = ${Protobuf_FOUND}")
message(STATUS "Protobuf_DIR = ${Protobuf_DIR}")
message(STATUS "Protobuf_PROTOC_EXECUTABLE = ${Protobuf_PROTOC_EXECUTABLE}")
message(STATUS "Protobuf_INCLUDE_DIRS = ${Protobuf_INCLUDE_DIRS}")
message(STATUS "Protobuf_LIBRARIES = ${Protobuf_LIBRARIES}")
message(STATUS "protobuf_INCLUDE_DIRS = ${protobuf_INCLUDE_DIRS}")
message(STATUS "protobuf_LIBRARIES = ${protobuf_LIBRARIES}")

file(GLOB_RECURSE PROTO_FILES ${CMAKE_CURRENT_SOURCE_DIR}/proto/*.proto)
message(STATUS "PROTO_FILES = ${PROTO_FILES}")
set(ALL_PROTO_SRCS)
set(ALL_PROTO_HDRS)
foreach(proto_file ${PROTO_FILES})
  protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${proto_file})
  message(STATUS "PROTO_SRCS = ${PROTO_SRCS}")
  message(STATUS "PROTO_HDRS = ${PROTO_HDRS}")
  list(APPEND ALL_PROTO_SRCS ${PROTO_SRCS})
  list(APPEND ALL_PROTO_HDRS ${PROTO_HDRS})
endforeach()

# 生成的文件在build目录下
message(STATUS "ALL_PROTO_SRCS = ${ALL_PROTO_SRCS}")
message(STATUS "ALL_PROTO_HDRS = ${ALL_PROTO_HDRS}")

add_library(hello src/hello.cpp ${ALL_PROTO_SRCS})

target_include_directories(hello PUBLIC 
  ${CMAKE_CURRENT_SOURCE_DIR}/include 
  ${protobuf_INCLUDE_DIRS}
  ${CMAKE_CURRENT_BINARY_DIR}
)

target_link_libraries(hello PUBLIC ${protobuf_LIBRARIES})

if(BUILD_MAIN)
  add_library(hello_main src/hello_main.cpp)
  target_include_directories(hello_main PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${protobuf_INCLUDE_DIRS}
    ${CMAKE_CURRENT_BINARY_DIR}
  )
  target_compile_definitions(hello_main PUBLIC HELLO_MAIN)
endif()

if(DEFINED BUILD_TESTING)
    message(STATUS "${CMAKE_CURRENT_LINE} HELLO BUILD_TESTING is defined: ${BUILD_TESTING}")
    if(BUILD_TESTING)
        message(FATAL_ERROR "${CMAKE_CURRENT_LINE} HELLO BUILD_TESTING is defined and set to ON")
    endif()
else()
    message(STATUS "${CMAKE_CURRENT_LINE} HELLO BUILD_TESTING is not defined")
endif()