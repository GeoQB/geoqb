import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyGeoQB",
    version="0.0.1",
    author="Mirko Kämpf",
    author_email="mirko.kaempf@gmail.com",
    description="Package to manage multi-layer property-graph data for contextual analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)