from os import path

from setuptools import find_packages, setup

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="intersection",
    description="Left turn in intersection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    python_requires=">=3.7",
    install_requires=[
        "setuptools>=41.0.0,!=50.0",
        "smarts[camera-obs] @ git+https://git@github.com/huawei-noah/SMARTS@example-ultra-31122021",
        "dreamerv2==2.2.0",
        "tensorflow==2.4.0",
        "tensorflow-probability==0.12.2",
    ],
)
