from cpt.packager import ConanMultiPackager

# https://docs.conan.io/1/creating_packages/package_tools.html
# https://github.com/conan-io/conan-package-tools

# A basic build.py for all most all the cases
if __name__ == "__main__":
    builder = ConanMultiPackager(build_policy="missing")

    # 构建指定setting/options等的包
    builder.add(
        settings={"build_type": "Debug"}, options={}, env_vars={}, build_requires={}
    )
    builder.add(
        settings={"build_type": "Release"}, options={}, env_vars={}, build_requires={}
    )

    # 自动选择所有组合形式的setting进行包构建，可以在创建builder的时候明确setting，构建只会基于这些setting进行组合
    # gcc_versions: Generate only build configurations for the specified gcc versions (Ignored if the current machine is not Linux)
    # visual_versions: Generate only build configurations for the specified Visual Studio versions (Ignore if the current machine is not Windows)
    # visual_runtimes: Generate only build configurations for the specified runtimes. (only for Visual Studio)
    # visual_toolsets: Specify the toolsets per each specified Visual Studio version. (only for Visual Studio)
    # msvc_versions: Generate only build configurations for the specified msvc versions (Ignore if the current machine is not Windows)
    # msvc_runtimes: Generate only build configurations for the specified runtimes. (only for msvc)
    # msvc_runtime_types: Specify the runtime types per each specified msvc version. (only for msvc)
    # apple_clang_versions: Generate only build configurations for the specified apple clang versions (Ignored if the current machine is not OSX)
    # archs: Generate build configurations for the specified architectures, by default, ["x86", "x86_64"].
    # build_types: Generate build configurations for the specified build_types, by default ["Debug", "Release"].
    # builder.add_common_builds()

    builder.run()
