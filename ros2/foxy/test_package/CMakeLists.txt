cmake_minimum_required(VERSION 3.5)
project(test_package)

find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(test_package test_package.cpp)

target_include_directories(test_package PUBLIC ${std_msgs_INCLUDE_DIRS})
target_link_libraries(test_package PRIVATE rclcpp::rclcpp ${std_msgs_LIBRARIES} std_msgs::std_msgs__rosidl_typesupport_cpp std_msgs::std_msgs__rosidl_typesupport_introspection_cpp)
