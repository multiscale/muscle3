import pathlib
from setuptools import find_packages, setup


_here = pathlib.Path(__file__).resolve().parent
_version_file = _here / 'VERSION'
with _version_file.open('r') as f:
    _version = f.read().strip()

# this is a hack, but it works for now and keeps the version number in a single file
_libmuscle_version_file = _here / 'libmuscle' / 'python' / 'libmuscle' / 'version.py'
with _libmuscle_version_file.open('w') as f:
    f.write('__version__ = \'{}\'\n'.format(_version))

_muscle3_packages = [
        p for p in find_packages() + find_packages('libmuscle/python')
        if p != 'integration_test']

_long_desc = (_here / 'README.rst').read_text()

setup(
    name='muscle3',
    version=_version,
    description='Version 3 of the MUltiScale Coupling Library and Environment',
    long_description=_long_desc,
    long_description_content_type='text/x-rst',
    author='Lourens Veen',
    author_email='l.veen@esciencecenter.nl',
    url='https://github.com/multiscale/muscle3',
    license='Apache License 2.0',
    keywords=['multiscale', 'coupling', 'MUSCLE'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        ],

    packages=_muscle3_packages,
    package_dir={
        'muscle3': 'muscle3',
        'libmuscle': 'libmuscle/python/libmuscle'
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'muscle_manager=muscle3.muscle_manager:manage_simulation',
            'muscle3=muscle3.muscle3:muscle3']
    },
    python_requires='>=3.8, <4',
    install_requires=[
        'click>=7.1,<9',
        'matplotlib>=3,<4',
        'msgpack>=1,<2',
        'psutil>=5.0.0',
        'parsimonious',
        "numpy>=1.22",
        'ymmsl>=0.14.0,<0.15'          # Also in CI, and examples requirements.txt
    ],
    extras_require={
        'dev': [
            'tox'
        ]
    },
)
