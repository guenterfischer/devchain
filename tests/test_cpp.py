
import pytest

import os
import shutil
import subprocess


@pytest.fixture(scope='session', autouse=True)
def directory(request):
    tmp_dir = '/tmp/pytest/devchain'

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    def cleanup():
        if os.path.exists(tmp_dir):
            # shutil.rmtree(tmp_dir)
            pass
    request.addfinalizer(cleanup)

    return tmp_dir


def test_create(directory):
    result = subprocess.run(
        'devchain create --toolchain cpp',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=directory
    )

    assert (0 == result.returncode)
    assert (0 == len(result.stderr))


def test_build(directory):
    result = subprocess.run(
        'devchain build --settings clang14__x86_64-pc-linux-elf__release',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=directory
    )

    assert (0 == result.returncode)


@pytest.mark.parametrize('tool', ['clang-tidy',
                                  'gtest',
                                  'benchmark',
                                  'asan',
                                  'msan',
                                  'tsan'])
def test_run(directory, tool):
    result = subprocess.run(
        'devchain run --tool {}'.format(tool),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=directory
    )

    assert (0 == result.returncode)
