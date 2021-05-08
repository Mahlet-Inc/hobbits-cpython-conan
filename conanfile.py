from conans import ConanFile, tools
import http.client
import json
import os

class HobbitsCpythonConan(ConanFile):
    name = "hobbits-cpython"
    version = "3.9.1"
    settings = "os", "compiler", "build_type", "arch"
    description = "A CPython build configured for embedding into Hobbits"
    url = "None"
    license = "PSF"
    author = "None"
    topics = None

    def build(self):
        # Get the latest build ID
        conn = http.client.HTTPSConnection("dev.azure.com")
        conn.request("GET", "/mahlet-inc/hobbits/_apis/build/builds?api-version=5.0&%24top=1&definitions=2")
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data)
        build_id = json_data['value'][0]['id']
        print(f"latest build ID: {build_id}")

        if self.settings.arch != "x86_64":
            raise NotImplementedError("Only x86_64 architecture is available")
        if self.settings.os == "Linux" and self.settings.compiler == "gcc" and self.settings.compiler.version == "4.8":
            artifact_name = "python_centos_74"
        elif self.settings.os == "Linux":
            artifact_name = "python_ubuntu_1804"
        elif self.settings.os == "Windows":
            artifact_name = "python_windows_2019"
        elif self.settings.os == "Macos":
            artifact_name = "python_macos_1014"

        url = f"https://dev.azure.com/mahlet-inc/hobbits/_apis/build/builds/{build_id}/artifacts?artifactName={artifact_name}&api-version=5.1&%24format=zip"
        tools.get(url, filename="python_binaries", strip_root=True)
        print(f"Current dir: {os.listdir()}")
        tools.unzip(f"{artifact_name}.tgz")

    def package(self):
        self.copy("*", excludes="*.tgz")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
