#include <iostream>
#include "nihao.h"

void nihao(){
    std::cout << "nihao/0.1: start----------------!" <<std::endl;
    hello();
    std::cout << "nihao/0.1: end----------------!" <<std::endl;
}

#ifdef ENABLE_L2
void nihao_l2(){
    std::cout << __FUNCTION__ << ":" << __LINE__ << ": this is nihao_l2" << std::endl;
}
#endif
