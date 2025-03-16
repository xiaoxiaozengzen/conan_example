from conan import ConanFile
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.cmake import CMakeDeps, CMakeToolchain

required_conan_version = ">=1.53.0"


class MyTestConan(ConanFile):
    name = "my_test"
    version = "dev"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _min_cppstd(self):
        return 14

    def configure(self):
        self.options["ros2"].enable_fastdds = False
        self.options["ros2"].with_rviz = True
        self.options["ros2"].with_rqt = True

    def requirements(self):
        # self.requires("rviz/foxy")
        # self.requires("vision_opencv/foxy")
        # self.requires("image_common/foxy")
        self.requires("libpng/1.6.44")
        self.requires("freetype/2.11.1")
        self.requires("zlib/1.2.13")
        self.requires("xkbcommon/1.4.1")
        self.requires("ros2/foxy20230620@transformer/stable")
 
    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualRunEnv(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")
