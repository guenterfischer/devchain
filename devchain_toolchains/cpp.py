#!/usr/bin/python3


import os
import re
import shutil
import subprocess
import glob

from importlib.resources import files

from .utils.types import ToolchainStatus
from .utils.types import ToolchainOption
from .utils.types import ToolchainInfo

from .utils.types import StatusCode
from .utils.types import Result


class Cpp:
    def __init__(self, directory: str):
        self.__root_directory = directory
        self.__build_directory = os.path.join(self.__root_directory, 'build')

        data = files('devchain_toolchains.data')
        self.__settings_dir = data.joinpath('cpp').joinpath('settings')
        self.__template_dir = data.joinpath('cpp').joinpath('template')

        self.__default_settings = 'clang14__x86_64-pc-linux-elf__release'

    def info(self) -> ToolchainInfo:
        '''
        Collects all infos about the given directory regarding CPP setup.

        Returns:
                Toolchain information
        '''
        info = ToolchainInfo(name='cpp')

        if not self.__has_cpp_toolchain():
            info.status = ToolchainStatus.NOT_AVAILABLE
            return info

        info.status = ToolchainStatus.AVAILABLE

        info.build_opts = []
        info.build_opts.append(
            ToolchainOption(name='settings', values=self.__settings()))

        info.run_opts = []
        info.run_opts.append(
            ToolchainOption(name='tool', values=self.__tools()))

        # TODO(gfischer)
        # Enhance verification

        return info

    def create(self) -> Result:
        '''
        Creates a new project setup.

        Returns:
            Result
        '''
        if len(os.listdir(self.__root_directory)) > 0:
            return Result(
                code=StatusCode.ERROR_INVALID_CONFIG,
                message='Target directory is not empty',
                info={
                    'root-directory': self.__root_directory,
                }
            )

        shutil.copytree(self.__template_dir,
                        self.__root_directory, dirs_exist_ok=True)
        return Result(
            code=StatusCode.SUCCESS,
            message='Project successfully set up',
            info={
                'root-directory': self.__root_directory,
            }
        )

    def clean(self) -> Result:
        '''
        Cleans the project setup.

        Returns:
            Result
        '''
        # Remove complete build directory
        if os.path.exists(self.__build_directory):
            shutil.rmtree(self.__build_directory)

        # Remove compile_commands.json
        compile_commands = os.path.join(
            self.__root_directory, 'compile_commands.json')
        if os.path.exists(compile_commands):
            os.remove(compile_commands)

        return Result(
            code=StatusCode.SUCCESS,
            message='Project cleanup successfully completed',
            info={
                'root-directory': self.__root_directory,
                'build-directory': self.__build_directory
            }
        )

    def build(self, settings: str, cmake_opts: list[str] = []) -> Result:
        '''
        Builds the project with the given settings.

        Parameters:
            settings (str): Settings to be used
        Returns:
            Result
        '''
        # Check user input
        if not self.__in_settings(settings):
            return Result(
                code=StatusCode.ERROR_INVALID_CONFIG,
                message='Unknown settings'
            )

        settings_path = os.path.join(self.__settings_dir, settings)
        if not os.path.exists(settings_path):
            return Result(
                code=StatusCode.ERROR_INVALID_CONFIG,
                message='Unknown settings'
            )

        # Build directory for this settings
        build_directory = os.path.join(self.__build_directory, settings)

        # Prepare environment
        if not os.path.exists(build_directory):
            os.makedirs(build_directory)

        # Install conan packages
        cmd = []
        cmd.append('conan install {}'.format(self.__root_directory))
        cmd.append('--output-folder {}'.format(build_directory))
        cmd.append('--profile:host {}'.format(settings_path))
        cmd.append('--profile:build {}'.format(settings_path))
        cmd.append('--build missing')

        presult = subprocess.run(
            ' '.join(cmd), shell=True, cwd=build_directory)
        if presult.returncode != 0:
            return Result(
                code=StatusCode.ERROR_COMMAND_FAILED,
                message='Failed to install conan packages'
            )

        # Prepare project
        cmake_toolchain = os.path.join(
            build_directory, 'conan_toolchain.cmake')
        if not os.path.exists(cmake_toolchain):
            return Result(
                code=StatusCode.ERROR_INVALID_CONFIG,
                message='conan_toolchain.cmake is missing'
            )
        cmd = []
        cmd.append('cmake')
        cmd.append('-DCMAKE_BUILD_TYPE={}'.format(self.__build_type(settings)))
        cmd.append('-DCMAKE_TOOLCHAIN_FILE={}'.format(cmake_toolchain))
        cmd.extend(cmake_opts)
        cmd.append(self.__root_directory)

        presult = subprocess.run(
            ' '.join(cmd), shell=True, cwd=build_directory)
        if presult.returncode != 0:
            return Result(
                code=StatusCode.ERROR_COMMAND_FAILED,
                message='Failed to prepare project'
            )

        # Build project
        cmd = []
        cmd.append('cmake')
        cmd.append('--build {}'.format(build_directory))
        cmd.append('-- -j')

        presult = subprocess.run(
            ' '.join(cmd), shell=True, cwd=build_directory)
        if presult.returncode != 0:
            return Result(
                code=StatusCode.ERROR_COMMAND_FAILED,
                message='Failed to prepare project'
            )

        # Copy compile_commands.json, if available
        compile_commands = os.path.join(
            build_directory, 'compile_commands.json')
        if os.path.exists(compile_commands):
            shutil.copy2(compile_commands, self.__root_directory)

        return Result(
            code=StatusCode.SUCCESS,
            message='Project successfully built',
            info={
                'root-directory': self.__root_directory,
                'build-directory': build_directory
            }
        )

    def run(self, tool: str) -> Result:
        '''
        Runs the specified tool within the project.

        Parameters:
            tool (str): Tool to be run
        Returns:
            Result
        '''
        # Check user input
        if not self.__in_tools(tool):
            return Result(
                code=StatusCode.ERROR_INVALID_CONFIG,
                message='Unknown tool'
            )

        # Run tool
        if tool == 'clang-tidy':
            return self.__run_clang_tidy()
        if tool == 'gtest':
            return self.__run_gtest()
        if tool == 'benchmark':
            return self.__run_benchmark()
        if tool == 'asan':
            return self.__run_xsan('asan')
        if tool == 'msan':
            return self.__run_xsan('msan')
        if tool == 'tsan':
            return self.__run_xsan('tsan')

        return Result(
            code=StatusCode.ERROR_INTERNAL,
            message='Internal error',
            info={
                'root-directory': self.__root_directory
            }
        )

    def __has_cpp_toolchain(self) -> bool:
        if not os.path.exists(self.__root_directory):
            return False

        cmake_root = os.path.join(self.__root_directory, 'CMakeLists.txt')
        if not os.path.exists(cmake_root):
            return False

        return True

    def __settings(self) -> list[str]:
        return os.listdir(self.__settings_dir)

    def __in_settings(self, settings) -> bool:
        for build_opt in self.info().build_opts:
            if build_opt.name == 'settings':
                if settings in build_opt.values:
                    return True
        return False

    def __build_type(self, settings) -> str:
        if m := re.match(r'.+__(\w+)$', settings):
            return m.group(1).upper()
        return ''

    def __tools(self) -> list[str]:
        return [
            'clang-tidy',
            'gtest',
            'benchmark',
            'asan',
            'msan',
            'tsan'
        ]

    def __in_tools(self, tool) -> bool:
        for run_opt in self.info().run_opts:
            if run_opt.name == 'tool':
                if tool in run_opt.values:
                    return True
        return False

    def __run_clang_tidy(self) -> Result:
        '''
        Cleans the project and then builds it with 'clang-tidy' enabled.
        '''
        result = self.clean()
        if not result.ok():
            return result

        result = self.build(self.__default_settings,
                            cmake_opts=['-DANALYSIS=clang-tidy'])
        return result

    def __run_gtest(self) -> Result:
        '''
        Runs all unit tests.
        Before the tests are executed, the project is built with default settings.
        '''
        # At first, build the project
        result = self.build(self.__default_settings)
        if not result.ok():
            return result

        # Build directory for this settings
        build_directory = os.path.join(
            self.__build_directory, self.__default_settings)

        # Create default result
        result = Result(
            code=StatusCode.SUCCESS,
            message='Tests successfully executed',
            info={
                'root-directory': self.__root_directory,
                'build-directory': build_directory
            }
        )

        # Run all tests
        for app in glob.glob('{}/**/*-test'.format(build_directory), recursive=True):
            presult = subprocess.run(app, shell=True)
            if presult.returncode != 0:
                result.code = StatusCode.ERROR_COMMAND_FAILED
                result.message = 'Failed to run gtest'
                result.info[os.path.basename(app)] = '[red]failed[/red]'
            else:
                result.info[os.path.basename(app)] = '[green]passed[/green]'

        return result

    def __run_benchmark(self) -> Result:
        '''
        Runs all benchmarks.
        Before the benchmarks are executed, the project is built with default settings.
        '''
        # At first, build the project
        result = self.build(self.__default_settings)
        if not result.ok():
            return result

        # Build directory for this settings
        build_directory = os.path.join(
            self.__build_directory, self.__default_settings)

        # Create default result
        result = Result(
            code=StatusCode.SUCCESS,
            message='Benchmarks successfully executed',
            info={
                'root-directory': self.__root_directory,
                'build-directory': build_directory
            }
        )

        # Run all tests
        for app in glob.glob('{}/**/*-bench'.format(build_directory), recursive=True):
            presult = subprocess.run(app, shell=True)
            if presult.returncode != 0:
                result.code = StatusCode.ERROR_COMMAND_FAILED
                result.message = 'Failed to run benchmark'
                result.info[os.path.basename(app)] = '[red]failed[/red]'
            else:
                result.info[os.path.basename(app)] = '[green]passed[/green]'

        return result

    def __run_xsan(self, sanitizer: str) -> Result:
        '''
        Cleans the project and then builds it with enabled sanitizer.
        Afterwards, all tests are run.
        '''
        result = self.clean()
        if not result.ok():
            return result

        result = self.build(self.__default_settings,
                            cmake_opts=['-DSANITIZER={}'.format(sanitizer)])
        if not result.ok():
            return result

        build_directory = result.info['build-directory']

        for app in glob.glob('{}/**/*-test'.format(build_directory), recursive=True):
            presult = subprocess.run(app, shell=True)
            if presult.returncode != 0:
                result.code = StatusCode.ERROR_COMMAND_FAILED
                result.message = 'Failed to run test'
                result.info[os.path.basename(app)] = '[red]failed[/red]'
            else:
                result.info[os.path.basename(app)] = '[green]passed[/green]'

        return result
