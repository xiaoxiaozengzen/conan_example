#include "hello.h"
#include "nihao.h"
#include "world.h"

#include <iostream>

int main(int argc, char** argv){
  hello();
  message();
  hello_main();
  #ifdef ENABLE_L2
  nihao_l2();
  #endif
  world();

  #ifdef ENABLE_L2_DEFINED
  #pragma message("ENABLE_L2_DEFINED is defined in test.cpp")
  std::cout << "ENABLE_L2_DEFINED is defined in test.cpp" << std::endl;
  #endif
}
