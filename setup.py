from setuptools import setup, find_packages

_version = open("VERSION").read().strip()

setup(
    name="cc.toolbox",
    version=_version,
    description="Control Center Toolbox",
    long_description=open("README.md").read(),
    classifiers=["Programming Language :: Python"],
    keywords="",
    author="Zenoss, Inc.",
    author_email="",
    url="https://github.com/control-center/toolbox",
    license="Apache",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["cc"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "kazoo",
        "docker"],
    entry_points={
        "console_scripts": [
            "dockerdisk=cc.toolbox.dockerdisk:main",
            "serviced-tool=cc.toolbox.tool:main",
        ],
    },
)
