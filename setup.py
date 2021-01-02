from setuptools import setup
import pathlib
import re

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")
# Remove gif - It won't be display correctly in PyPi
long_description = re.sub(r"!\[Clipster demo\].+?\)", "", long_description)

setup(
    name="clipster-desktop",
    version="0.4.3",
    description="Multi Platform Cloud Clipboard - Desktop Client",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="http://github.com/mc51/Clipster-Desktop",
    author="MC51",
    author_email="mc@data-dive.com",
    license="MIT",
    packages=["clipster"],
    install_requires=[
        "requests",
        "pyperclip",
        "PySide2",
        "PySimpleGUI",
        "PySimpleGUIQt",
        "cryptography",
    ],
    python_requires=">=3.6",
    zip_safe=False,
    entry_points={"console_scripts": ["clipster = clipster.clipster:main"]},
    package_data={"icon": ["resources/clipster.ico"],},
    classifiers=[
        "Topic :: Desktop Environment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: System",
        "Topic :: Security :: Cryptography",
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="clipster, clipboard, cryptography, secure, copy&paste, cloud, clipboard manager, data dive",
    project_urls={
        "Bug Reports": "https://github.com/mc51/Clipster-Desktop/issues",
        "Source": "https://github.com/mc51/Clipster-Desktop/",
        "Developer Website": "https://data-dive.com",
    },
)
