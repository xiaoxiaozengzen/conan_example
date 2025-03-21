from conans import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import (
    export_conandata_patches,
    apply_conandata_patches,
    copy,
    save,
)
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conans.tools import collect_libs

import os
import shutil
from typing import Any


class WorldConan(ConanFile):
    name = "world"
    version = "0.1"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Hello here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    user = "cgz"
    channel = "demo"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["hello"].calib3d = False

    def requirements(self):
        self.requires("hello/1.1.1@cgz/demo")

    def layout(self):
        pass

    def export_sources(self):
        self.copy(
            "include/*",
            dst=os.path.join(self.export_sources_folder),
            src=os.path.join(os.getcwd()),
        )
        self.copy(
            "CMakeLists.txt",
            dst=self.export_sources_folder,
            src=os.path.join(os.getcwd()),
        )
        self.copy(
            "src/*",
            dst=os.path.join(self.export_sources_folder),
            src=os.path.join(os.getcwd()),
        )

    def source(self):
        save(self, os.path.join(self.source_folder, "external.h"), "#pragma once \n#include <iostream>")

    # 会去找layout中设置的source路径下的CMakeLists.txt
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    # 目前看起来他会source_folder和build_folder中的文件都拷贝到package_folder中
    def package(self):
        self.copy(
            "*.h",
            dst="include",
            src=os.path.join(self.source_folder, "include"),
            keep_path=True,
        )
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "World")
        self.cpp_info.set_property("cmake_target_name", "World::world")
        self.cpp_info.set_property("pkg_config_name", "World")
        self.cpp_info.libs = collect_libs(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
