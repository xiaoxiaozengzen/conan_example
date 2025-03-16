#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto message = std_msgs::msg::String();
  message.data = "Hello, world!";
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Publishing: '%s'", message.data.c_str());
  rclcpp::shutdown();
  return 0;
}