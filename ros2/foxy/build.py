import os
from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    # conancenter上的gcc10的spdlog用了glibc2.30里的`pthread_cond_clockwait`,
    # 会导致编译失败, 所以设置默认重新编译
    builder = ConanMultiPackager(build_policy=["missing", "spdlog", "fast-dds"])
    builder.add_common_builds(pure_c=False)
    builder.run()
