#include <iostream>
#include "hello.h"

void hello_main(){
    #ifdef NDEBUG
    std::cout << "hello/0.1: Hello World Release! hello_main" <<std::endl;
    #else
    std::cout << "hello/0.1: Hello World Debug!  hello_main" <<std::endl;
    #endif
}
