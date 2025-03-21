cmake_minimum_required(VERSION 3.1)
project(nihao CXX)

# find_package(hello REQUIRED)

if(ENABLE_L2)
    message(STATUS "ENABLE_L2 is ON")
    add_compile_definitions(ENABLE_L2)
endif()

add_library(nihao SHARED src/nihao.cpp)
target_include_directories(
    nihao PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_INCLUDE_PATH}
)

install(TARGETS nihao
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/ DESTINATION include)

