#pragma once

#include <thread>
#include <iostream>
#include <chrono>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
#include <visualization_msgs/msg/marker.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <geometry_msgs/msg/point.hpp>

#include "rclcpp/rclcpp.hpp"
#include "devastator_perception_msgs/msg/my_test.hpp"

namespace cgz {
using MyTest = devastator_perception_msgs::msg::MyTest;
using Marker = visualization_msgs::msg::Marker;
using MarkerArray = visualization_msgs::msg::MarkerArray;

class MyPub : public rclcpp::Node {
public:
    MyPub(const rclcpp::NodeOptions& options);
    ~MyPub();

    void Init();

    rclcpp::Publisher<MyTest>::SharedPtr publisher_{nullptr};
    // rclcpp::TimerBase::SharedPtr timer_{nullptr};
    rclcpp::Publisher<MarkerArray>::SharedPtr marker_pub_{nullptr};

    std::thread send_th_;
};
}

