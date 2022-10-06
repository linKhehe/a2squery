import re
from setuptools import setup


def read_requirements(filename):
    try:
        with open(filename) as f:
            return f.read().split("\n")
    except FileNotFoundError:
        return []


with open("a2squery/__init__.py") as f:
    version = re.search(r"__version__ *= *[\"'](.*)[\"']", f.read()).group(1)

with open("README.md") as f:
    readme = f.read()

requirements = read_requirements("requirements.txt")
extras_require = {
    "docs": read_requirements("docs/requirements.txt")
}

setup(name="a2squery",
      author="linKhehe",
      url="https://github.com/linKhehe/a2squery",
      project_urls={
        "Documentation": "https://a2squery.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/linKhehe/a2squery/issues",
      },
      version=version,
      license="MIT",
      description="A2SQuery is a python implementation of Valve's A2S protocol",
      long_description=readme,
      long_description_content_type="text/markdown",
      install_requires=requirements,
      extras_require=extras_require,
      include_package_data=True,
      python_requires=">=3.6.0",
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
      ]
)
