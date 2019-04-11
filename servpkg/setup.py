import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="srvpkg-theo",
    version="0.0.1",
    author="Theophile et Marine",
    author_email="theophile.moreal-de-brevans@insa-lyon.fr",
    description="Package du projet reseau",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MorealDeBrevans/deploiement",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
