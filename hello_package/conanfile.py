from conans import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import (
    export_conandata_patches,
    apply_conandata_patches,
    copy,
    save,
)
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conans.tools import os_info, SystemPackageTool

import os
import shutil
from typing import Any

required_conan_version = ">=1.27.1"

HELLO_MAIN_MODULES_OPTIONS = (("calib3d", True), ("dnn", False))


class HelloConan(ConanFile):
    name = "hello"
    version = "1.1.1"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Hello here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "number": ["default", "first"],
        "calib3d": [True, False],
        "with_test": [True, False],
        "with_main": [True, False],
    }
    options.update({_name: [True, False] for _name, _ in HELLO_MAIN_MODULES_OPTIONS})
    default_options = {"shared": True, "fPIC": True, "number": "default", "calib3d": True, "with_test": False, "with_main": True}
    default_options.update(
        {_name: select for _name, select in HELLO_MAIN_MODULES_OPTIONS}
    )
    user = "cgz"
    channel = "demo"
    # no_copy_source=True
    python_requires = "gtest/1.13.0@transformer/stable" # 复用gtest的conanfile.py中的某些module

    # 在创建包的时候，会调用该方法，用于设置包的属性，其先于configure调用
    # 在其他人install该包的时候，其中option会被修改。例如self.options.number会被修改成其他值
    def config_options(self):
        print("hello config_options: pwd=", os.getcwd())
        if self.settings.os == "Windows":
            del self.options.fPIC
        # self.options.number = "first"

    # 在创建包的时候，会调用该方法，用于设置包的属性，其后于configure_options调用
    # 在其他人install该包的时候，其中设置的option不会被修改。例如self.options.number不会被修改
    def configure(self):
        print("hello configure: pwd=", os.getcwd())
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # self.options.number = "first"

    def validate(self):
        print("hello validate: pwd=", os.getcwd())
        print("hello validate: self.settings.arch", self.settings.arch)
        print("hello validate: self.options.shared", self.options.shared)
        print("hello validate: self.settings.build_type", self.settings.build_type)
        print("hello validate: self.options.number", self.options.number)
        # if self.options.number != "default":
        #     raise ConanInvalidConfiguration("self.options.number is not default")
    
    # This section refers to the feature that is activated when using --profile:build and --profile:host in the command-line.    
    def build_requirements(self):
        print("hello build_requirements: pwd=", os.getcwd())
        # New since Conan 1.60.
        self.tool_requires("protobuf/<host_version>")

    def system_requirements(self):
        print("hello system_requirements: pwd=", os.getcwd())
        pack_name = "cpulimit"
        if self.settings.os == "Linux":
            installer = SystemPackageTool()
            installer.install(pack_name)
        print("hello system_requirements: os_info.is_linux=", os_info.is_linux)

    def requirements(self):
        print("hello requirements: pwd=", os.getcwd())
        self.requires("gtest/1.13.0@transformer/stable", override=True)
        self.requires("yaml-cpp/0.8.0")
        self.requires("protobuf/3.21.12")

    # In the layout() method you can adjust self.folders and self.cpp.
    def layout(self):
        # 重新配置source folder
        cmake_layout(self, src_folder="src2")
        print("hello layout: pwd=", os.getcwd())
        print("hello layout: self.folders.root=", self.folders.root)
        print("hello layout: self.folders.source=", self.folders.source)
        print("hello layout: self.folders.build=", self.folders.build)
        
        # 该文件目录下是requries中的包的*.cmake以及conanrun.sh文件
        print("hello layout: self.folders.generators=", self.folders.generators)
        print("hello layout: self.folders.imports=", self.folders.imports)
        
    
    # 控制生成包的package id
    # Default package ID is calculated using settings, options and requires properties.
    # This self.info object stores the information that will be used to compute the package ID. 
    def package_id(self):
        print("hello package_id: pwd=", os.getcwd())
        print("hello package_id: self.self_info.requires[yaml-cpp].full_name=", self.info.requires["yaml-cpp"].full_name)
        print("hello package_id: self.self_info.requires[yaml-cpp].full_version=", self.info.requires["yaml-cpp"].full_version)
        print("hello package_id: self.self_info.requires[yaml-cpp].full_user=", self.info.requires["yaml-cpp"].full_user)
        print("hello package_id: self.self_info.requires[yaml-cpp].full_channel=", self.info.requires["yaml-cpp"].full_channel)
        print("hello package_id: self.self_info.requires[yaml-cpp].full_package_id=", self.info.requires["yaml-cpp"].full_package_id)
        self.info.clear()

    def export(self):
        # 本地conanfile.py所在的路径
        print("hello export: pwd=", os.getcwd())
        print("hello export: export_folder=", self.export_folder)
        print("hello export: export_sources_folder=", self.export_sources_folder)
        print("hello export: source_folder=", self.source_folder)
        print("hello export: build_folder=", self.build_folder)
        print("hello export: package_folder=", self.package_folder)
        print("hello export: install_folder=", self.install_folder)
        print("hello export: recipe_folder=", self.recipe_folder)
        # The self.copy support src and dst subfolder arguments.
        # The src is relative to the current folder (the one containing the conanfile.py).
        # The dst is relative to the cache export_folder.
        self.copy("test.py")

    # 如果设置layout，不影响该方法，其直接从export_sources_folder复制到"<package_id>/source",而不是self.source_folder
    def export_sources(self):
        # 本地conanfile.py所在的路径
        print("hello export_sources: pwd=", os.getcwd())
        print("hello export_sources: export_folder=", self.export_folder)
        print("hello export_sources: export_sources_folder=", self.export_sources_folder)
        print("hello export_sources: source_folder=", self.source_folder)
        print("hello export_sources: build_folder=", self.build_folder)
        print("hello export_sources: package_folder=", self.package_folder)
        print("hello export_sources: install_folder=", self.install_folder)
        print("hello export_sources: recipe_folder=", self.recipe_folder)
        # The self.copy support src and dst subfolder arguments.
        # The src is relative to the current folder (the one containing the conanfile.py).
        # The dst is relative to the cache export_sources_folder.
        try:
            # 注释掉的都是没法成功复制的
            # self.copy("src")
            # self.copy("src/")
            self.copy(
                "*",
                dst=os.path.join(self.export_sources_folder, "src1"),
                src=os.path.join(os.getcwd(), "hello"),
            )
        except:
            print("hello +++++++++++++++++++++++++export_sources: copy error")
        else:
            print("hello +++++++++++++++++++++++++export_sources: copy ok")

        export_conandata_patches(self)

    # <package_id>/source文件夹会先直接拷贝<package_id>/export_source，与layout设置与否无关
    def source(self):
        print("hello source: pwd=", os.getcwd())
        print("hello source: export_folder=", self.export_folder)
        print("hello source: export_sources_folder=", self.export_sources_folder)
        print("hello source: source_folder=", self.source_folder)
        print("hello source: build_folder=", self.build_folder)
        print("hello source: package_folder=", self.package_folder)
        print("hello source: install_folder=", self.install_folder)
        print("hello source: recipe_folder=", self.recipe_folder)
        copy(
            self,
            "*",
            src=os.path.join(self.export_sources_folder, "src1"),
            dst=self.source_folder,
            keep_path=True,
        )
        save(
            self,
            path=os.path.join(self.export_sources_folder, "source.h"),
            content=f"#include <iostream>\n",
        )

    # 会去找layout中设置的source路径下的CMakeLists.txt
    def build(self):
        print("hello build: path= ", self.python_requires["gtest"].path)
        self.output.success("This is a good, should be green")
        self.output.info("This is a neutral, should be white")
        self.output.warn("This is a warning, should be yellow")
        self.output.error("Error, should be red")
        print("hello build: pwd=", os.getcwd())
        print("hello build: export_folder=", self.export_folder)
        print("hello build: export_sources_folder=", self.export_sources_folder)
        print("hello build: source_folder=", self.source_folder)
        print("hello build: build_folder=", self.build_folder)
        print("hello build: package_folder=", self.package_folder)
        print("hello build: install_folder=", self.install_folder)
        print("hello build: recipe_folder=", self.recipe_folder)

        print("hello build: self.settings.build_type=", self.settings.build_type)
        print("hello build: self.settings.os=", self.settings.os)
        print("hello build: self.settings.compiler=", self.settings.compiler)
        print("hello build: self.settings.compiler.version=", self.settings.compiler.version)
        print("hello build: self.settings.compiler.libcxx=", self.settings.compiler.libcxx)
        print("hello build: self.settings.arch=", self.settings.arch)
        print("hello build: self.options.number=", self.options.number)

        # build: source_folder中的源码就会应用patch
        apply_conandata_patches(self)

        print("hello version: ", self.version)
        print("hello ", self.conan_data)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    # 目前看起来他会source_folder和build_folder中的文件都拷贝到package_folder中
    def package(self):
        print("hello package: pwd=", os.getcwd())
        print("hello package: export_folder=", self.export_folder)
        print("hello package: export_sources_folder=", self.export_sources_folder)
        print("hello package: source_folder=", self.source_folder)
        print("hello package: build_folder=", self.build_folder)
        print("hello package: package_folder=", self.package_folder)
        print("hello package: install_folder=", self.install_folder)
        print("hello package: recipe_folder=", self.recipe_folder)
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
        self.cpp_info.set_property("cmake_file_name", "HEllo")

        # # 不会生成find_package查找的Cmake相关的文件了
        # self.cpp_info.set_property("cmake_find_mode", "none")

        # self.cpp_info.set_property("cmake_target_name", "hello")
        # self.cpp_info.libs = ["hello"]
        
        # hello
        self.cpp_info.components["libhello"].set_property(
            "cmake_target_name", "HEllo::hello"
        )
        self.cpp_info.components["libhello"].set_property(
            "cmake_target_aliases", ["HEllo::hello"]
        )
        self.cpp_info.components["libhello"].set_property(
            "pkg_config_name", "hello"
        )
        self.cpp_info.components["libhello"].libs = [f"hello"]
        # don't work, why?
        self.cpp_info.components["libhello"].defines = ["HELLO"]

        if self.options.with_main:
          # hello_main
          self.cpp_info.components["libhello_main"].set_property(
              "cmake_target_name", "HEllo::hello_main"
          )
          self.cpp_info.components["libhello_main"].set_property(
              "cmake_target_aliases", ["HEllo::hello_main"]
          )
          self.cpp_info.components["libhello_main"].set_property(
              "pkg_config_name", "hello_main"
          )
          self.cpp_info.components["libhello_main"].libs = [f"hello_main"]

        self.env_info.WORLD = "WORLD"
        self.runenv_info.define("HELLO_TEST", "HAHAHA")
        self.buildenv_info.append_path(
            "PATH", os.path.join(self.package_folder, "build_bin")
        )
        self.runenv_info.prepend_path(
            "PATH", os.path.join(self.package_folder, "run_bin")
        )
        print("hello package_info: self.dependencies[yaml-cpp].package_folder", self.dependencies["yaml-cpp"].package_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if self.options.with_test:
            tc.variables["BUILD_TESTING"] = True
        else:
            tc.variables["BUILD_TESTING"] = False
        if self.options.with_main:
            tc.variables["BUILD_MAIN"] = True
        else:
            tc.variables["BUILD_MAIN"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        tc = VirtualRunEnv(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    # The deploy() method is designed to work on a package that is installed directly from its reference,
    # 直接将package安装到当前目录下，而不是local cache中
    def deploy(self):
        self.copy("*.so*", src="lib", dst="bin")
        self.copy("*.a", src="lib", dst="bin")
