import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "iou",
    version = "0.1",
    author = "James J. Porter",
    author_email = "porterjamesj@gmail.com",
    description = "personal debt management for you and your friends",
    license = "MIT",
    keywords = "iou debts personal",
    url = "https://github.com/porterjamesj/iou",
    longdescription=read("README.rst"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
    py_modules = ["debtgraph"],
    scripts = ["iou"],
)
