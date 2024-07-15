from setuptools import setup, find_packages

setup(
    name="menucmd",
    version="1.00.1",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    author="Casey Litmer",
    author_email="litmerc@msn.com",
    description="Command line menu interface",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Casey-Litmer/menucmd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
