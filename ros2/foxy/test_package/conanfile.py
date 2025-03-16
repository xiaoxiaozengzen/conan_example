from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"
    options = {"with_rviz": [True, False], "with_rqt": [True, False]}
    default_options = {"with_rviz": False, "with_rqt": False}

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)
        # workaround for https://github.com/conan-io/conan/issues/11891
        self.folders.build = (
            "build_"
            + str(self.settings.build_type)
            + "_"
            + str(self.settings.compiler.libcxx)
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
