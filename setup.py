from setuptools import setup

setup(
    name='MUSCLE 3',
    version='0.0.0.dev',
    description='Version 3 of the MUltiScale Coupling Library and Environment',
    author='Lourens Veen',
    author_email='l.veen@esciencecenter.nl',
    url='https://github.com/multiscale/muscle3',
    license='Apache License 2.0',
    keywords=['multiscale', 'coupling', 'MUSCLE'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'],

    packages=['muscle_manager', 'libmuscle'],
    package_dir={
        'muscle_manager': 'muscle_manager',
        'libmuscle': 'libmuscle/python/libmuscle'
    },
    python_requires='>=3.5, <4',
    install_requires=[
        'grpcio==1.10.0',
        'ymmsl==0.2.1'
    ],
    setup_requires=[
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'recommonmark',
        'sphinx-rtd-theme'
    ],
    tests_require=[
        'coverage<5',
        'mypy',
        'pytest>=3.5',
        'pytest-cov',
        'pytest-pep8',
        'pytest-flake8',
        'pytest-mypy'
    ],
    extras_require={
        'dev': [
            'grpcio-tools==1.10.0',
            'sphinx',
            'sphinx_rtd_theme==0.2.4',
            'yapf',
            'isort'
        ]
    },
)
