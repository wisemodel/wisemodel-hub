from setuptools import find_packages, setup


def get_version() -> str:
    rel_path = "src/wisemodel_hub/__init__.py"
    with open(rel_path, "r") as fp:
        for line in fp.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


install_requires = [
    "packaging>=20.9",
    "requests>=2.20.0",
    "tqdm>=4.64.1",
    "python-gitlab>=5.0.0",
    "ipywidgets>=8.1.5",
]

extras = {}

extras["torch"] = [
    "torch",
    "safetensors[torch]",
]

# Typing extra dependencies list is duplicated in `.pre-commit-config.yaml`
# Please make sure to update the list there when adding a new typing dependency.
extras["typing"] = [
    "typing-extensions>=4.8.0",
    "types-PyYAML",
    "types-requests",
    "types-simplejson",
    "types-toml",
    "types-tqdm",
    "types-urllib3",
]

extras["quality"] = [
    "ruff>=0.5.0",
    "mypy==1.5.1",
    "libcst==1.4.0",
]

extras["doc"] = [
    "sphinx>=8.1.0",
    "sphinx-autobuild>=2024.10.3",
    "sphinx_rtd_theme>=3.0.0",
    "myst_parser>=4.0.0",
    "sphinx-markdown-tables>=0.0.17",
]

extras["all"] = extras["quality"] + extras["typing"] + extras["doc"]

extras["dev"] = extras["all"]

entry_points = {
    "console_scripts": [
        "wm_upload=wisemodel_hub.upload_script:wm_upload",
        "wm_download=wisemodel_hub.download_script:wm_download",
    ],
}

setup(
    name="wisemodel_hub",
    version=get_version(),
    author="始智AI",
    author_email="4498237@qq.com",
    description="Client library to download and publish models, datasets and other repos on the wisemodel.cn hub",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="model-hub machine-learning models natural-language-processing deep-learning pytorch pretrained-models",
    license="Apache",
    url="https://github.com/wisemodel/wisemodel-hub",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require=extras,
    python_requires=">=3.8.0",
    install_requires=install_requires,
    entry_points=entry_points,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
)
