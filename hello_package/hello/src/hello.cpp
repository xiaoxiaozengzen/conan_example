#include <iostream>

#include <google/protobuf/util/time_util.h>
#include "proto/message.pb.h"

#include "hello.h"


void hello(){
    #ifdef NDEBUG
    std::cout << "hello/0.1: Hello World Release!" <<std::endl;
    #else
    std::cout << "hello/0.1: Hello World Debug!" <<std::endl;
    #endif

    #ifdef HELLO_DEFINE
    std::cout << "hello/1.1.1: Hello Define!" <<std::endl;
    #endif
}

void message() {
  InputOutputDataProto::Quaternion qua;
  qua.set_qw(10);
  std::cout << "InputOutputDataProto::Quaternion::qw : " << qua.qw() << std::endl;
}
