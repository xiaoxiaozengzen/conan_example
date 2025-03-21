#pragma once

#include "hello.h"

void nihao();

#ifdef ENABLE_L2_DEFINED
#pragma message("ENABLE_L2_DEFINED is defined in nihao.h")
void nihao_l2_defined();
#endif

#ifdef ENABLE_L2
#pragma message("ENABLE_L2 is defined in nihao.h")
void nihao_l2();
#endif

