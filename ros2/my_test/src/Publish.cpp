#include <csignal>
#include <rclcpp/rclcpp.hpp>
#include "my_test/Publish.hpp"

namespace cgz {
MyPub::MyPub(const rclcpp::NodeOptions& options)
    :Node("my_test_node", options) {
        publisher_ =
            this->create_publisher<MyTest>("/my/test", 10);
        marker_pub_ =
            this->create_publisher<MarkerArray>("/my/marker", 10);

        send_th_ = std::thread(std::bind(&MyPub::Init, this));

        // timer_ = this->create_wall_timer(std::chrono::milliseconds(50), std::bind(&MyPub::Init, this));
    }

MyPub::~MyPub() {
    if (send_th_.joinable()) {
        send_th_.join();
    }
}

void MyPub::Init() {
    while(rclcpp::ok()) {
        MyTest msg;
        msg.a = 0x10;
        msg.b = 0x20;
        // msg.c = true;

        publisher_->publish(msg);

        MarkerArray marker_array;
        int marker_id = 0;

        for(int i = 0; i < 100; i++) {
            Marker marker;
            marker.header.frame_id = "map";
            marker.header.stamp = rclcpp::Clock().now();
            marker.action = visualization_msgs::msg::Marker::ADD;
            marker.lifetime.sec = 0;
            marker.lifetime.nanosec = 1e7;

            geometry_msgs::msg::Point arrow_point;
            arrow_point.x = 0;
            arrow_point.y = 0;
            arrow_point.z = 0;
            marker.points.push_back(arrow_point);

            geometry_msgs::msg::Point arrow_sz;
            arrow_sz.x = 100;
            arrow_sz.y = 0;
            arrow_sz.z = 0;
            marker.points.push_back(arrow_sz);

            marker.id = marker_id++;
            marker.type = visualization_msgs::msg::Marker::ARROW;
            marker.scale.x = 1;
            marker.scale.y = 0.5;
            marker.scale.z = 0.5;

            marker.color.r = 255;
            marker.color.b = 0;
            marker.color.g = 0;
            marker.color.a = 1.0;

            marker_array.markers.push_back(marker);
        }

        marker_pub_->publish(marker_array);

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

}
}




// int main(int argc, char** argv) {

//   auto single_handle = [](int sig) {
//     (void)sig;
//     rclcpp::shutdown();
//   };
//   signal(SIGINT, single_handle);

//   rclcpp::init(argc, argv);
//   rclcpp::spin(std::make_shared<Pub>());
//   rclcpp::shutdown();

//   return 0;
// }

#include "rclcpp_components/register_node_macro.hpp"  // NOLINT

RCLCPP_COMPONENTS_REGISTER_NODE(cgz::MyPub)