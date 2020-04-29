import setuptools

with open("README.md", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyplume",
    version="0.0.1",
    author="Anthony Walker",
    author_email="walkanth@oregonstate.edu",
    license='BSD 3-clause "New" or "Revised License"',
    description="This package contains files to build models for exhaust plume analysis and methods to analyze the results.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SoftwareDevEngResearch/plume-generation-and-analysis",
    entry_points={
        'console_scripts': [
            'pyplume.mech=pyplume.mech:mechCLI'
        ]
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
