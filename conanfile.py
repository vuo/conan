from conans import ConanFile

class VuoUtilsConan(ConanFile):
    name = 'vuoutils'
    version = '1.2'
    url = 'https://github.com/vuo/conan'
    license = 'https://github.com/vuo/conan/blob/master/LICENSE'
    description = "Common resources for Vuo's Conan packages"
    exports = '*'
    build_policy = "missing"

    def package(self):
        self.copy('*.py')

    def package_info(self):
        self.env_info.PYTHONPATH.append(self.package_folder)
