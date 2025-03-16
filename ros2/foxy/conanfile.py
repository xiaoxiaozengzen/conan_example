import os
import sys
import glob
from shutil import which
import shutil
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    download,
    export_conandata_patches,
    chdir,
    copy,
    mkdir,
    rmdir,
    rename,
    replace_in_file,
)
import tempfile
from conan.tools.scm import Git
from conans.tools import os_info, SystemPackageTool
import subprocess


def _python_version():
    return "python{major}.{minor}".format(
        major=sys.version_info[0], minor=sys.version_info[1]
    )


os.environ["PATH"] += os.pathsep + os.path.join(
    os.path.expanduser("~"), ".local", "bin"
)


class ROS2Conan(ConanFile):
    name = "ros2"
    version = "foxy20230620"
    user = "transformer"
    channel = "stable"
    license = "Apache-2.0"
    url = "https://github.com/ros2/ros2"
    description = " The Robot Operating System, is a meta operating system for robots."
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cyclonedds": [True, False],
        "enable_fastdds": [True, False],
        "with_rviz": [True, False],
        "with_rqt": [True, False],
        "with_test": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "enable_cyclonedds": True,
        "enable_fastdds": True,
        "with_rviz": False,
        "with_rqt": False,
        "with_test": False,
        "tinyxml/*:with_stl": True,
        "ogre/*:shared": True,
        "qt/*:shared": True,
        "qt/*:qtsvg": True,
        "qt/*:with_mysql": False,
    }
    no_copy_source = True
    ignores = []

    def export_sources(self):
        copy(self, "ignore_list", self.recipe_folder, self.export_sources_folder)
        copy(
            self,
            "mcap_x86",
            os.path.join(self.recipe_folder, "mcap_bin"),
            os.path.join(self.export_sources_folder),
        )
        
        copy(
            self,
            "mcap_orin",
            os.path.join(self.recipe_folder, "mcap_bin"),
            os.path.join(self.export_sources_folder),
        )
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Neutrino":
            self.options["libcurl"].with_ssl = False

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux is supported")

        if not self.options.enable_cyclonedds and not self.options.enable_fastdds:
            raise ConanInvalidConfiguration(
                "at least enable one rmw implementation, cycloneeds or fastdds"
            )
        if (
            self.options.enable_cyclonedds
            and self.options.enable_fastdds
            and not self.options.shared
        ):
            raise ConanInvalidConfiguration(
                "enable multiple dds implementations but static linking was requested"
            )

    def requirements(self):
        if self.options.with_rviz:
            self.requires("libpng/1.6.39")
            self.requires("freetype/2.12.1")
            self.requires("xkbcommon/1.4.1")
        self.requires("spdlog/1.9.2")
        self.requires("zlib/1.2.13")
        self.requires("tinyxml/2.6.2")
        self.requires("tinyxml2/9.0.0")
        self.requires("pybind11/2.9.1")
        self.requires(
            "console_bridge/1.0.1", transitive_headers=True, transitive_libs=True
        )
        if self.settings.os != "Neutrino":
            self.requires("mimick/0.2.6@ros2/stable")
        self.requires("yaml-cpp/0.7.0")
        self.requires("libyaml/0.2.5", transitive_headers=True, transitive_libs=True)
        self.requires("zstd/1.5.2")
        self.requires("sqlite3/3.39.4")
        self.requires("eigen/3.4.0")
        self.requires("readerwriterqueue/1.0.6")
        self.requires("bullet3/3.17")
        self.requires("libcurl/7.80.0")
        if self.settings.os != "Neutrino":
            self.requires("openssl/[>=1.1 <4]")
        self.requires("foonathan-memory/0.7.3@transformer/stable")
        if self.options.enable_cyclonedds:
            self.requires("cyclonedds/0.7.0")
        if self.options.enable_fastdds:
            self.requires(
                "fast-cdr/1.0.26", transitive_headers=True, transitive_libs=True
            )
            self.requires(
                "fast-dds/2.3.4@transformer/stable",
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_rviz:
            # self.requires("qt/5.15.2")
            self.requires("opengl/system")
            self.requires("ogre/1.12.13")
            self.requires("assimp/5.1.0")
            self.requires("pugixml/1.12.1")
        if self.options.with_test:
            self.requires("gtest/1.11.0")
            self.requires("benchmark/1.6.0")

    # see https://github.com/colcon/colcon-ros/issues/130
    def _patch_colcon(self):
        import subprocess

        self.output.warning("try to patching colcon_ros...")
        try:
            # colcon-common-extensions may be just installed in system requirements,
            # so we need to find it in another process
            dir = subprocess.check_output(
                f'{sys.executable} -c "import colcon_ros; print(colcon_ros.__path__[0])"',
                shell=True,
                encoding="utf-8",
            )
            dir = dir.strip()
            subprocess.check_call(
                [
                    "sudo",
                    "sed",
                    "-i",
                    "s/subprocess.CalledProcessError/Exception/g",
                    os.path.join(dir, "task", "cmake", "__init__.py"),
                ]
            )
        except Exception as e:
            self.output.warning(e)
            
    def _is_package_installed(self, package_name):
        """check if package is installed"""
        result = subprocess.run(
            ["dpkg", "-l", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return package_name in result.stdout.decode()


    def system_requirements(self):
        packages = {
            "colcon": "colcon-common-extensions",
            "vcs": "vcstool",
        }  # exe_name, package_name
        for exe_name, package_name in packages.items():
            abs_path = which(exe_name)
            if abs_path is None:
                self.run(f"{sys.executable} -m pip install {package_name}")
        self._patch_colcon()
        self.run(f"{sys.executable} -m pip install lark numpy")
        if self.settings.os == "Neutrino":
            self.run(f'{sys.executable} -m pip install "cython<3"')
        if self.options.with_rqt:
            self.run(f"{sys.executable} -m pip install PyQt5 pydot")
            
        if self.options.with_rviz:            
            package_names = [
                "libfreetype6-dev",
                "libfreeimage-dev",
                "libzzip-dev",
                "libxrandr-dev",
                "libxaw7-dev",
                "freeglut3-dev",
                "libgl1-mesa-dev",
                "libglu1-mesa-dev",
                "qtbase5-dev",
                "qtdeclarative5-dev",
            ]
            installer = SystemPackageTool()
            for pack_name in package_names:
                if not self._is_package_installed(pack_name):
                    print(f"Package {pack_name} is not installed. Installing...")
                    installer.install(
                        pack_name
                    )  # Install the package, will update the package database if pack_name isn't already installed


    def _colcon_build(self, cmake_args=None):
        colcon_args = [
            f"--build-base={os.path.join(self.build_folder, 'build')}",
            f"--install-base={self.package_folder}",
            f"--packages-ignore {' '.join(self.ignores)}",
            "--merge-install",
            "--cmake-clean-cache",
        ]

        if cmake_args is not None:
            cmake_args_string = " ".join(cmake_args)
            colcon_args.append("--cmake-args {args}".format(args=cmake_args_string))

        colcon_args_string = " ".join(colcon_args)
        with chdir(self, self.source_folder):
            print("colcon build {args}".format(args=colcon_args_string))
            self.run("colcon build {args}".format(args=colcon_args_string))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        # ignore specific packages
        with open(os.path.join(self.export_sources_folder, "ignore_list"), "r") as f:
            content = f.read()
        files_list = content.splitlines()
        self._colcon_ignore_packages(self.workspace_dir, files_list)
        apply_conandata_patches(self)
        if not self.options.shared:
            replace_in_file(
                self,
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/rosidl_defaults/rosidl_default_generators/package.xml",
                ),
                r"<buildtool_export_depend>rosidl_generator_py</buildtool_export_depend>",
                "",
            )
            replace_in_file(
                self,
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/rosidl_python/rosidl_generator_py/CMakeLists.txt",
                ),
                r'ament_index_register_resource("rosidl_generator_packages")',
                "",
            )
        if self.settings.os == "Neutrino":
            replace_in_file(
                self,
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/unique_identifier_msgs/package.xml",
                ),
                r"<buildtool_depend>rosidl_default_generators</buildtool_depend>",
                "<buildtool_depend>rosidl_default_generators</buildtool_depend>\n  <buildtool_depend>numpy_vendor</buildtool_depend>",
            )
            replace_in_file(
                self,
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/rmw_dds_common/rmw_dds_common/package.xml",
                ),
                r"<buildtool_depend>rosidl_default_generators</buildtool_depend>",
                "<buildtool_depend>rosidl_default_generators</buildtool_depend>\n  <buildtool_depend>numpy_vendor</buildtool_depend>",
            )
            for file in glob.glob(
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/rcl_interfaces/*/package.xml",
                )
            ):
                replace_in_file(
                    self,
                    file,
                    r"<buildtool_depend>rosidl_default_generators</buildtool_depend>",
                    "<buildtool_depend>rosidl_default_generators</buildtool_depend>\n  <buildtool_depend>numpy_vendor</buildtool_depend>",
                )
            for file in glob.glob(
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/common_interfaces/*_msgs/package.xml",
                )
            ):
                replace_in_file(
                    self,
                    file,
                    r"<buildtool_depend>rosidl_default_generators</buildtool_depend>",
                    "<buildtool_depend>rosidl_default_generators</buildtool_depend>\n  <buildtool_depend>numpy_vendor</buildtool_depend>",
                )
            for file in glob.glob(
                os.path.join(
                    self.source_folder,
                    "source_subfolder/ros2/common_interfaces/*_srvs/package.xml",
                )
            ):
                replace_in_file(
                    self,
                    file,
                    r"<buildtool_depend>rosidl_default_generators</buildtool_depend>",
                    "<buildtool_depend>rosidl_default_generators</buildtool_depend>\n  <buildtool_depend>numpy_vendor</buildtool_depend>",
                )
            # replace_in_file(
            #     self,
            #     os.path.join(self.source_folder, "source_subfolder/numpy_vendor/CMakeLists.txt"),
            #     r"${CMAKE_INSTALL_PREFIX}/usr/lib/python3.8/site-packages",
            #     r"${CMAKE_INSTALL_PREFIX}/lib/python3.8/site-packages",
            # )

    def _configure_ignore(self):
        if not self.options.with_rqt:
            self.ignores.extend(
                [
                    "python_qt_binding",
                    "rqt",
                    "rqt_console",
                    "rqt_msg",
                    "rqt_publisher",
                    "rqt_reconfigure",
                    "rqt_shell",
                    "rqt_top",
                    "qt_gui_core",
                    "rqt_action",
                    "rqt_graph",
                    "rqt_plot",
                    "rqt_py_console",
                    "rqt_service_caller",
                    "rqt_srv",
                    "rqt_topic",
                ]
            )
        if not self.options.with_rviz:
            self.ignores.extend(
                [
                    "rviz2",
                    "rviz_common",
                    "rviz_default_plugins",
                    "rviz_rendering",
                    "rviz_rendering_tests",
                ]
            )
        if not self.options.enable_fastdds:
            self.ignores.extend(
                [
                    "rosidl_typesupport_fastrtps_cpp",
                    "rosidl_typesupport_fastrtps_c",
                    "rmw_fastrtps_shared_cpp",
                    "rmw_fastrtps_cpp",
                    "rmw_fastrtps_dynamic_cpp",
                ]
            )
        if not self.options.enable_cyclonedds:
            self.ignores.extend(
                [
                    "rmw_cyclonedds_cpp",
                ]
            )
        if self.settings.os == "Neutrino":
            self.ignores.extend(
                [
                    "rttest",
                    "tlsf_cpp",
                ]
            )

        return self.ignores

    def source(self):
        self.workspace_dir = os.path.join(self.source_folder, self._source_subfolder)
        self.repos_file_url = self.conan_data["sources"][self.version]["url"]
        self.repos_file_path = os.path.join(self.source_folder, "ros2.repos")
        download(self, self.repos_file_url, filename=self.repos_file_path)
        replace_in_file(
            self,
            self.repos_file_path,
            r"version: 0.3.11",
            r"version: foxy-future",  # update ros2cli to keep compatibility with ros installed by apt-get
        )
        if self.settings.os == "Neutrino":
            # add numpy in ros2.repos
            with open(self.repos_file_path, "a") as f:
                f.write(
                    """
  numpy_vendor:
    type: git
    url: https://gitlab.com/qnx/frameworks/ros2/numpy_vendor.git
    version: master"""
                )
        mkdir(self, self.workspace_dir)
        self.run(
            f"vcs import --shallow --retry 5 {self.workspace_dir} < {self.repos_file_path}"
        )
        self._patch_sources()
        
        tmp_dir = tempfile.TemporaryDirectory()
        git = Git(self)
        git.clone(
            "https://github.com/ros2/rosbag2.git",
            args=[tmp_dir.name, "--depth", "1", "-b", "0.15.4"],
        )
        if not os.path.exists(tmp_dir.name):
            raise ConanInvalidConfiguration("Failed to mkdir tmp_dir: {tmp_dir.name}")
               
        if not os.path.exists(os.path.join(tmp_dir.name, "mcap_vendor")):
            raise ConanInvalidConfiguration("There is no mcap_vendor in {tmp_dir.name}")
        
        if not os.path.exists(os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2")):
            raise ConanInvalidConfiguration("There is no {self.source_folder}/source_subfolder/ros2/rosbag2")
            
        shutil.copytree(os.path.join(tmp_dir.name, "mcap_vendor"), os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "mcap_vendor"))
        if os.path.exists(os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "rosbag2_storage_mcap")):
            shutil.rmtree(os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "rosbag2_storage_mcap"))
        shutil.copytree(os.path.join(tmp_dir.name, "rosbag2_storage_mcap"), os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "rosbag2_storage_mcap"))
        replace_in_file(
            self,
            os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "mcap_vendor", "CMakeLists.txt"),
            f"find_package(zstd_vendor REQUIRED)",
            "",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "source_subfolder", "ros2", "rosbag2", "mcap_vendor", "CMakeLists.txt"),
            f"ament_export_dependencies(zstd_vendor zstd)",
            f"ament_export_dependencies(zstd)",
        )


    def _colcon_ignore_packages(self, work_dir, packages):
        """
        Given a list of directories relative to work_dir, adds an empty file named
        COLCON_IGNORE in each of them. The colcon build tool looks for these files and skips
        the directories where they are found.
        """
        with chdir(self, work_dir):
            for ignore_item in packages:
                self.run(f"touch {os.path.join(ignore_item, 'COLCON_IGNORE')}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        self._configure_ignore()
        if self.settings.os == "Neutrino":
            replace_in_file(
                self,
                os.path.join(self.generators_folder, "conan_toolchain.cmake"),
                "set(CMAKE_SYSTEM_PROCESSOR armv8)",
                "set(CMAKE_SYSTEM_PROCESSOR aarch64le)",
            )
            qnx_target = os.environ.get("QNX_TARGET")
            qnx_host = os.environ.get("QNX_HOST")
            cmake_args = [
                "-DBUILD_TESTING=OFF",
                f"-DCMAKE_TOOLCHAIN_FILE={os.path.join(self.generators_folder, 'conan_toolchain.cmake')}",
                f"-DCMAKE_BUILD_TYPE={self.settings.build_type}",
                f"-DCMAKE_POSITION_INDEPENDENT_CODE={self.options.get_safe('fPIC', True)}",
                "-DPYTHON_SOABI=cpython-38",
                f"-DPYTHON_INCLUDE_DIR={qnx_target}/usr/include/python3.8\;{qnx_target}/usr/include/aarch64le/python3.8\;{qnx_target}/usr/include/python3.8\;{self.package_folder}/usr/lib/python3.8/site-packages/numpy/core/include",
                f"-DPYTHON_INCLUDE_DIRS={qnx_target}/usr/include/python3.8\;{qnx_target}/usr/include/aarch64le/python3.8\;{qnx_target}/usr/include/python3.8\;{self.package_folder}/usr/lib/python3.8/site-packages/numpy/core/include",
                f"-DPYTHON_LIBRARY={qnx_target}/aarch64le/usr/lib/libpython3.8.so",
                f"-DPYTHON_LIBRARIES={qnx_target}/aarch64le/usr/lib",
                f"-DPYTHONLIBS_FOUND=1",
                f"-DPYTHON_MODULE_EXTENSION=.cpython-38.so",
                f"-DCMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES={qnx_target}/usr/include",
                f"-DCPUVARDIR=aarch64le",
                f"-DQNX_TARGET={qnx_target}",
                f"-DCMAKE_STRIP={qnx_host}/usr/bin/ntoaarch64-strip",
            ]
        else:
            cmake_args = [
                "-DBUILD_TESTING=OFF",
                f"-DCMAKE_TOOLCHAIN_FILE={os.path.join(self.generators_folder, 'conan_toolchain.cmake')}",
                f"-DPython3_EXECUTABLE={which(sys.executable)}",
                f"-DPYTHON_EXECUTABLE={which(sys.executable)}",
                f"-DCMAKE_BUILD_TYPE={self.settings.build_type}",
                f"-DCMAKE_POSITION_INDEPENDENT_CODE={self.options.get_safe('fPIC', True)}",
            ]
            if cross_building(self):
                if self.settings.arch == "armv8" and self.settings.os == "Linux":
                    cmake_args.append(
                        f"-DPYTHON_SOABI=cpython-{sys.version_info[0]}{sys.version_info[1]}-aarch64-linux-gnu"
                    )
        if not self.options.shared:
            cmake_args.append("-DRMW_IMPLEMENTATION_DISABLE_RUNTIME_SELECTION=ON")
        self._colcon_build(cmake_args)

    def replace_shebang(self):
        def _get_files_from_install(install_prefix):
            paths_to_files = []

            bin_path = os.path.join(install_prefix, "bin")
            if os.path.exists(bin_path):
                bin_contents = [
                    os.path.join(bin_path, name) for name in os.listdir(bin_path)
                ]
                paths_to_files.extend(
                    [path for path in bin_contents if os.path.isfile(path)]
                )

            # Demo nodes are installed to 'lib/<package_name>'
            lib_path = os.path.join(install_prefix, "lib")
            if os.path.exists(lib_path):
                for lib_sub_dir in next(os.walk(lib_path))[1]:
                    sub_dir_path = os.path.join(lib_path, lib_sub_dir)
                    sub_dir_contents = [
                        os.path.join(sub_dir_path, name)
                        for name in os.listdir(sub_dir_path)
                    ]
                    paths_to_files.extend(
                        [path for path in sub_dir_contents if os.path.isfile(path)]
                    )

            return paths_to_files

        paths_to_files = _get_files_from_install(self.package_folder)
        for path in paths_to_files:
            with open(path, "rb") as h:
                content = h.read()
            shebang = b"#!%b" % sys.executable.encode("utf8")
            if content[0 : len(shebang)] != shebang:
                continue
            if self.settings.os == "Linux":
                # in the linux case
                new_shebang = b"#!/usr/bin/env python3"
                with open(path, "wb") as h:
                    h.write(new_shebang)
                    h.write(content[len(shebang) :])
            elif self.settings.os == "Neutrino":
                # in the qnx case
                new_shebang = b"#!/usr/bin/python3"
                with open(path, "wb") as h:
                    h.write(new_shebang)
                    h.write(content[len(shebang) :])

    def update_setup_files(self):
        replace_in_file(
            self,
            os.path.join(
                self.package_folder,
                "share/rosbag2_compression_zstd/cmake/export_rosbag2_compression_zstdExport.cmake",
            ),
            self.dependencies["zstd"].cpp_info.includedirs[0],
            "${zstd_INCLUDE_DIRS}",
        )
        replace_in_file(
            self,
            os.path.join(
                self.package_folder,
                "share/mcap_vendor/cmake/mcapExport.cmake",
            ),
            self.dependencies["zstd"].cpp_info.includedirs[0],
            "${zstd_INCLUDE_DIRS}",
        )
        if(os.path.exists(os.path.join(self.package_folder, "share/rviz_rendering/cmake/rviz_renderingExport.cmake"))):
            replace_in_file(
                self,
                os.path.join(
                    self.package_folder,
                    "share/rviz_rendering/cmake/rviz_renderingExport.cmake",
                ),
                self.dependencies["assimp"].cpp_info.includedirs[0],
                "${assimp_INCLUDE_DIRS}",
            )
        replace_in_file(
            self,
            os.path.join(self.package_folder, "local_setup.sh"),
            f'_colcon_prefix_sh_COLCON_CURRENT_PREFIX="{self.package_folder}"',
            '_colcon_prefix_sh_COLCON_CURRENT_PREFIX=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}" )" &> /dev/null && pwd )',
        )
        replace_in_file(
            self,
            os.path.join(self.package_folder, "setup.sh"),
            f"_colcon_prefix_chain_sh_COLCON_CURRENT_PREFIX={self.package_folder}",
            '_colcon_prefix_chain_sh_COLCON_CURRENT_PREFIX=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}" )" &> /dev/null && pwd )',
        )

        for setup_file in glob.glob(
            os.path.join(self.package_folder, "share", "*/local_setup.sh")
        ):
            replace_in_file(
                self,
                setup_file,
                f'${{AMENT_CURRENT_PREFIX:="{self.package_folder}"}}',
                '${AMENT_CURRENT_PREFIX:=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}" )" &> /dev/null && pwd )',
            )
        for setup_file in glob.glob(
            os.path.join(self.package_folder, "share", "*/package.sh")
        ):
            replace_in_file(
                self,
                setup_file,
                f'_colcon_package_sh_COLCON_CURRENT_PREFIX="{self.package_folder}"',
                '_colcon_package_sh_COLCON_CURRENT_PREFIX=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}" )" &> /dev/null && pwd )/../..',
            )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        self.replace_shebang()
        self.update_setup_files()
        with chdir(self, self.package_folder):
            os.symlink(".", "cmake")
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        
        if self.settings.arch == "x86_64":
            shutil.copyfile(
                os.path.join(self.export_sources_folder, "mcap_x86"),
                os.path.join(self.package_folder, "bin", "mcap"),
            )
            os.chmod(os.path.join(self.package_folder, "bin", "mcap"), 0o755)
        if self.settings.arch == "armv8":
            shutil.copyfile(
                os.path.join(self.export_sources_folder, "mcap_orin"),
                os.path.join(self.package_folder, "bin", "mcap"),
            )
            os.chmod(os.path.join(self.package_folder, "bin", "mcap"), 0o755)

    def append_env(self, key, value):
        getattr(self.env_info, key).append(value)
        self.runenv_info.append_path(key, value)
        self.buildenv_info.append_path(key, value)

    def set_env(self, key, value):
        setattr(self.env_info, key, value)
        self.runenv_info.define_path(key, value)
        self.buildenv_info.define_path(key, value)

    def package_info(self):
        python_dir = os.path.join(
            self.package_folder, "lib", _python_version(), "site-packages"
        )
        self.append_env("PYTHONPATH", python_dir)
        bin_dir = os.path.join(
            self.package_folder,
            "bin",
        )
        self.append_env("PATH", bin_dir)
        self.append_env("AMENT_PREFIX_PATH", self.package_folder)
        self.append_env("COLCON_PREFIX_PATH", self.package_folder)
        self.set_env("ROS_DISTRO", "foxy")
        self.set_env("ROS_PYTHON_VERSION", "3")
        self.set_env("ROS_VERSION", "2")
        if self.options.with_rviz:
            self.set_env("OGRE_PATH", self.dependencies["ogre"].package_folder)

        # self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs = ["cmake"]
