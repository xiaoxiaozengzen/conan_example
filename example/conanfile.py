from conans import ConanFile, CMake, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">=1.53.0"


class ExampleConan(ConanFile):
    name = "example"
    version = "1.0.0"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Hello here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_test": [True, False],
    }
    default_options = {
        "with_test": False,
    }

    def configure(self):
        self.options["hello"].number = "default"
        print("ExampleConan configure: number=", self.options["hello"].number)
        self.options["nihao"].with_l2 = True

    def requirements(self):
        # 按照顺序找依赖，nihao和world都会分别再install下hello，因此下边总共会调用三次hello中的configure_options和configure以及requirements
        # 并且如果同一个options在configure中出现两次，会直接报错：tried to change，but it was already assigned
        # 下面中就会报错：
        #    ERROR: hello/0.1@cgz/demo: world/0.1@cgz/demo tried to change hello/0.1@cgz/demo option number to default
        #    but it was already assigned to default by nihao/0.1@cgz/demo
        self.requires("hello/1.1.1@cgz/demo")
        self.requires("nihao/0.1@cgz/demo")
        self.requires("world/0.1@cgz/demo")
        self.requires("protobuf/3.21.12")

    def generate(self):
        # 访问依赖package的环境变量
        print(
            'self.deps_env_info["protobuf"].PATH = ',
            self.deps_env_info["protobuf"].PATH,
        )
        print(
            'self.deps_env_info["protobuf"].SONAME = ',
            self.deps_env_info["protobuf"].SONAME,
        )  # 环境变量不存在，改变量未NONE
        print(
            'self.deps_env_info["hello"].HELLO_TEST = ',
            self.deps_env_info["hello"].HELLO_TEST,
        )
        print('self.deps_env_info["hello"].WORLD = ', self.deps_env_info["hello"].WORLD)

        # 访问当前的环境变量
        print('os.environ["PATH"] = ', os.environ["PATH"])
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if self.options.with_test:
            tc.variables["BUILD_TESTING"] = True
        else:
            tc.variables["BUILD_TESTING"] = False
        if self.options["hello"].with_main:
            tc.variables["BUILD_MAIN"] = True        
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualRunEnv(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def imports(self):
        self.copy("*.so*", src="@libdirs", dst="lib", keep_path=True)
        self.copy("*.a", src="@libdirs", dst="lib", keep_path=True)
        self.copy("*", src="@bindirs", dst="bin", keep_path=True)
