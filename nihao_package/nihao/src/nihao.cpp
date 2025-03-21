#include <iostream>
#include "nihao.h"

void nihao(){
    std::cout << "nihao/0.1: start----------------!" <<std::endl;
    hello();
    std::cout << "nihao/0.1: end----------------!" <<std::endl;
}

#ifdef ENABLE_L2
#pragma message("ENABLE_L2 is defined in nihao.cpp")
void nihao_l2(){
    std::cout << __FUNCTION__ << ":" << __LINE__ << ": this is nihao_l2" << std::endl;
}
#endif


#ifdef ENABLE_L2_DEFINED
#pragma message("ENABLE_L2_DEFINED is defined in nihao.cpp")
void nihao_l2_defined(){
    std::cout << __FUNCTION__ << ":" << __LINE__ << ": this is nihao_l2_defined" << std::endl;
}
#endif