# -*- coding: utf-8 -*-
# @author: leesoar
# @email: secure@tom.com
# @email2: employ@aliyun.com

from os.path import join, isfile
from os import walk
import io
import os
import sys
from shutil import rmtree
from setuptools import setup, Command


def read_file(filename):
    with open(filename) as fp:
        return fp.read().strip()


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


NAME = 'dlna'
FOLDER = 'dlna'
DESCRIPTION = 'A UPnP/DLNA client, support local file and online resource cast to screen.'
URL = 'https://leesoar.com/real'
EMAIL = 'core@111.com'
AUTHOR = 'leesoar'
REQUIRES_PYTHON = '>=3.3.0'

REQUIRED = read_requirements('requirements.txt')

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


def package_files(directories):
    paths = []
    for item in directories:
        if isfile(item):
            paths.append(join('..', item))
            continue
        for (path, directories, filenames) in walk(item):
            for filename in filenames:
                paths.append(join('..', path, filename))
    return paths


class UploadCommand(Command):
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    version="0.2.2",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['dlna'],
    package_data={'dlna': ['templates/*.xml']},
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    entry_points={
        'console_scripts': ['dlna = dlna.client:run']
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    cmdclass={
        'upload': UploadCommand,
    },
    keywords=[
        'dlna'
    ],
)
