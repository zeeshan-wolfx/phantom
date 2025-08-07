from setuptools import setup, find_packages

setup(
    name='phantom',
    version='0.1.0',
    packages=find_packages(),       # this will pick up the phantom/ dir
    include_package_data=True,
    install_requires=[
        'click',
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            'phantom=phantom.cli:main',
        ],
    },
    author='The Beast',
    description='Deployment tool for Django, React, Next.js apps',
)