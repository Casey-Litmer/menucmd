from setuptools import setup, find_packages

setup(
    name="menucmd",
    version="1.2.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "menucmd": ["pyinstaller/**/*"],  # include all files in pyinstaller
    },
    author="Casey Litmer",
    author_email="litmerc@msn.com",
    description="Command line menu interface",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Casey-Litmer/menucmd",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "macrolibs",
        "pyinstaller==6.19"
    ],
    python_requires='>=3.6',
)
