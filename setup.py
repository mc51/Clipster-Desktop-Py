from setuptools import setup

setup(
    name="clipster-desktop",
    version="0.4.1",
    description="Multi Platform Cloud Clipboard - Desktop Client",
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
    ],
    python_requires=">=3.6",
    zip_safe=False,
    entry_points={"console_scripts": ["clipster = clipster.clipster:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
