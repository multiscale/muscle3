from setuptools import setup
setup(
        name = 'MUSCLE 3',
        packages = ['muscle_manager', 'libmuscle/python/libmuscle'],
        version = 'develop',
        description = 'Version 3 of the MUltiScale Coupling Library and Environment',
        url = 'https://github.com/multiscale/muscle3',
        download_url = 'https://github.com/multiscale/muscle3/archive/develop.tar.gz',
        license = 'Apache License 2.0',
        keywords = ['multiscale', 'coupling', 'MUSCLE'],
        classifiers = [
            'Development Status :: 1 - Planning',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'],

        python_requires='>=3.5, <4',
        install_requires=[],
        extras_require={
            'dev': []
            },
        )
