from setuptools import setup, find_packages

setup(
    name = 'jcc',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url = 'https://github.com/0x0L/jcc.git',
    author = '0x0L',
    author_email = '0x0L@github.com',
    description = 'Jupyter Contents Client',
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['jcc=jcc.cli:main'],
    },
    install_requires = ['requests', 'tqdm'],
)
