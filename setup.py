from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="enhanced-auto-committer",
    version="0.1.0-alpha",
    author="sreevarshan-xenoz",
    author_email="sreevarshan1511@gmail.com",
    description="An enhanced auto-committer for Git repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sreevarshan-xenoz/Auto-Committer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "auto-committer=auto_committer:main",
        ],
    },
) 