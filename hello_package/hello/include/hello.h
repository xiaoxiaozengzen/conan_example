#pragma once

#include <google/protobuf/util/time_util.h>
#include "proto/message.pb.h"

#ifdef WIN32
  #define hello_EXPORT __declspec(dllexport)
#else
  #define hello_EXPORT
#endif

hello_EXPORT void hello();
// hello_EXPORT void hello_main();

void message();
