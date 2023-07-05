from conan import ConanFile


class CppExample(ConanFile):

    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires("gtest/1.13.0")
        self.requires("benchmark/1.8.0")

    def imports(self):
        self.copy("license*", dst="licenses", folder=True, ignore_case=True)
