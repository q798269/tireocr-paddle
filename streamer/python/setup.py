#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# This file refered to github.com/onnx/onnx.git

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import shutil
import os

TOP_DIR = os.path.realpath(os.path.dirname(__file__))
TOP_DIR = os.path.split(TOP_DIR)[0]
PACKAGE_NAME = os.getenv("PACKAGE_NAME", "streamer")
wheel_name = "fastdeploy-streamer-python"

from distutils.spawn import find_executable
from distutils import sysconfig, log
import setuptools
import setuptools.command.build_py
import setuptools.command.develop
import setuptools.command.build_ext

from collections import namedtuple
from contextlib import contextmanager
import glob
import shlex
import subprocess
import sys
import platform
from textwrap import dedent
import multiprocessing

setup_configs = dict()
setup_configs["PY_LIBRARY_NAME"] = "fastdeploy" + PACKAGE_NAME + "_main"

print(TOP_DIR, 'top dir--')

SRC_DIR = os.path.join(TOP_DIR, 'python')
PYTHON_SRC_DIR = os.path.join(TOP_DIR, 'python', "streamer")
CMAKE_BUILD_DIR = os.path.join(TOP_DIR, 'python', '.setuptools-cmake-build')
FASTDEPLOY_INSTALL_DIR = os.path.join(TOP_DIR, '../build', 'installed_fastdeploy')

WINDOWS = (os.name == 'nt')

CMAKE = find_executable('cmake3') or find_executable('cmake')
MAKE = find_executable('make')

setup_requires = []
extras_require = {}

################################################################################
# Version
################################################################################

try:
    git_version = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=TOP_DIR).decode('ascii').strip()
except (OSError, subprocess.CalledProcessError):
    git_version = None

with open(os.path.join(TOP_DIR, '..', 'VERSION_NUMBER')) as version_file:
    VersionInfo = namedtuple('VersionInfo', ['version', 'git_version'])(
        version=version_file.read().strip(), git_version=git_version)

################################################################################
# Pre Check
################################################################################

assert CMAKE, 'Could not find "cmake" executable!'

################################################################################
# Utilities
################################################################################


@contextmanager
def cd(path):
    if not os.path.isabs(path):
        raise RuntimeError('Can only cd to absolute path, got: {}'.format(path))
    orig_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(orig_path)

################################################################################
# Customized commands
################################################################################
class ONNXCommand(setuptools.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


def get_all_files(dirname):
    files = list()
    for root, dirs, filenames in os.walk(dirname):
        for f in filenames:
            fullname = os.path.join(root, f)
            files.append(fullname)
    return files


class create_version(ONNXCommand):
    def run(self):
        with open(os.path.join(PYTHON_SRC_DIR, 'code_version.py'), 'w') as f:
            f.write(
                dedent('''\
            # This file is generated by setup.py. DO NOT EDIT!
            from __future__ import absolute_import
            from __future__ import division
            from __future__ import print_function
            from __future__ import unicode_literals
            version = '{version}'
            git_version = '{git_version}'
            '''.format(**dict(VersionInfo._asdict()))))


class cmake_build(setuptools.Command):
    """
    Compiles everything when `python setupmnm.py build` is run using cmake.
    Custom args can be passed to cmake by specifying the `CMAKE_ARGS`
    environment variable.
    The number of CPUs used by `make` can be specified by passing `-j<ncpus>`
    to `setup.py build`.  By default all CPUs are used.
    """
    user_options = [(str('jobs='), str('j'),
                     str('Specifies the number of jobs to use with make'))]

    built = False

    def initialize_options(self):
        self.jobs = None

    def finalize_options(self):
        if sys.version_info[0] >= 3:
            self.set_undefined_options('build', ('parallel', 'jobs'))
        if self.jobs is None and os.getenv("MAX_JOBS") is not None:
            self.jobs = os.getenv("MAX_JOBS")
        self.jobs = multiprocessing.cpu_count() if self.jobs is None else int(
            self.jobs)

    def run(self):
        if cmake_build.built:
            return
        cmake_build.built = True
        if not os.path.exists(CMAKE_BUILD_DIR):
            os.makedirs(CMAKE_BUILD_DIR)

        with cd(CMAKE_BUILD_DIR):
            build_type = 'Release'
            # configure
            cmake_args = [
                CMAKE,
                '-DPYTHON_INCLUDE_DIR={}'.format(sysconfig.get_python_inc()),
                '-DPYTHON_EXECUTABLE={}'.format(sys.executable),
                '-DBUILD_FDSTREAMER_PYTHON=ON',
                '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
                '-DPY_EXT_SUFFIX={}'.format(
                    sysconfig.get_config_var('EXT_SUFFIX') or ''),
                '-DFASTDEPLOY_INSTALL_DIR={}'.format(FASTDEPLOY_INSTALL_DIR),
            ]
            cmake_args.append('-DCMAKE_BUILD_TYPE=%s' % build_type)
            for k, v in setup_configs.items():
                cmake_args.append("-D{}={}".format(k, v))
            if 'CMAKE_ARGS' in os.environ:
                extra_cmake_args = shlex.split(os.environ['CMAKE_ARGS'])
                # prevent crossfire with downstream scripts
                del os.environ['CMAKE_ARGS']
                log.info('Extra cmake args: {}'.format(extra_cmake_args))
                cmake_args.extend(extra_cmake_args)
            cmake_args.append(TOP_DIR)
            subprocess.check_call(cmake_args)

            build_args = [CMAKE, '--build', os.curdir]
            if WINDOWS:
                build_args.extend(['--config', build_type])
                build_args.extend(['--', '/maxcpucount:{}'.format(self.jobs)])
            else:
                build_args.extend(['--', '-j', str(self.jobs)])
            subprocess.check_call(build_args)


class build_py(setuptools.command.build_py.build_py):
    def run(self):
        self.run_command('create_version')
        self.run_command('cmake_build')

        generated_python_files = \
            glob.glob(os.path.join(CMAKE_BUILD_DIR, PACKAGE_NAME, '*.py')) + \
            glob.glob(os.path.join(CMAKE_BUILD_DIR, PACKAGE_NAME, '*.pyi'))

        for src in generated_python_files:
            dst = os.path.join(TOP_DIR, os.path.relpath(src, CMAKE_BUILD_DIR))
            self.copy_file(src, dst)

        return setuptools.command.build_py.build_py.run(self)


class develop(setuptools.command.develop.develop):
    def run(self):
        self.run_command('build_py')
        setuptools.command.develop.develop.run(self)


class build_ext(setuptools.command.build_ext.build_ext):
    def run(self):
        self.run_command('cmake_build')
        setuptools.command.build_ext.build_ext.run(self)

    def build_extensions(self):
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            filename = os.path.basename(self.get_ext_filename(fullname))

            lib_path = CMAKE_BUILD_DIR
            if os.name == 'nt':
                debug_lib_dir = os.path.join(lib_path, "Debug")
                release_lib_dir = os.path.join(lib_path, "Release")
                if os.path.exists(debug_lib_dir):
                    lib_path = debug_lib_dir
                elif os.path.exists(release_lib_dir):
                    lib_path = release_lib_dir
            src = os.path.join(lib_path, filename)
            dst = os.path.join(
                os.path.realpath(self.build_lib), PACKAGE_NAME, filename)
            self.copy_file(src, dst)

class mypy_type_check(ONNXCommand):
    description = 'Run MyPy type checker'

    def run(self):
        """Run command."""
        onnx_script = os.path.realpath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tools/mypy-onnx.py"))
        returncode = subprocess.call([sys.executable, onnx_script])
        sys.exit(returncode)


cmdclass = {
    'create_version': create_version,
    'cmake_build': cmake_build,
    'build_py': build_py,
    'develop': develop,
    'build_ext': build_ext,
    'typecheck': mypy_type_check,
}

################################################################################
# Extensions
################################################################################

ext_modules = [
    setuptools.Extension(
        name=str(PACKAGE_NAME + '.' + setup_configs["PY_LIBRARY_NAME"]),
        sources=[]),
]

################################################################################
# Packages
################################################################################

# no need to do fancy stuff so far
# if PACKAGE_NAME != "fastdeploy_streamer":
#     packages = setuptools.find_packages(exclude=['fastdeploy*', 'scripts'])
# else:
packages = setuptools.find_packages(exclude=['scripts'])

################################################################################
# Test
################################################################################

if sys.version_info[0] == 3:
    # Mypy doesn't work with Python 2
    extras_require['mypy'] = ['mypy==0.600']

################################################################################
# Final
################################################################################

package_data = {PACKAGE_NAME: []}

if sys.argv[1] == "install" or sys.argv[1] == "bdist_wheel":
    from scripts.process_libraries import process_libraries
    all_lib_data = process_libraries(
        os.path.split(os.path.abspath(__file__))[0])
    package_data[PACKAGE_NAME].extend(all_lib_data)
    print("Package_data:")
    print(all_lib_data)
    setuptools.setup(
        name=wheel_name,
        version=VersionInfo.version,
        ext_modules=ext_modules,
        description="Deploy Kit Tool For Deeplearning models.",
        packages=packages,
        package_data=package_data,
        include_package_data=True,
        setup_requires=setup_requires,
        extras_require=extras_require,
        author='fastdeploy',
        author_email='fastdeploy@baidu.com',
        url='https://github.com/PaddlePaddle/FastDeploy.git',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        license='Apache 2.0')
else:
    setuptools.setup(
        name=wheel_name,
        version=VersionInfo.version,
        description="Deploy Kit Tool For Deeplearning models.",
        ext_modules=ext_modules,
        cmdclass=cmdclass,
        packages=packages,
        package_data=package_data,
        include_package_data=False,
        setup_requires=setup_requires,
        extras_require=extras_require,
        author='fastdeploy',
        author_email='fastdeploy@baidu.com',
        url='https://github.com/PaddlePaddle/FastDeploy.git',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        license='Apache 2.0')
