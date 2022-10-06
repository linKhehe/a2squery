from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(name="a2squery",
      author="linKhehe",
      url="https://github.com/linKhehe/a2squery",
      project_urls={
        "Documentation": "https://a2squery.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/linKhehe/a2squery/issues",
      },
      version="0.0.1",
      license="MIT",
      description="A2SQuery is a python implementation of Valve's A2S protocol",
      long_description=readme,
      long_description_content_type="text/x-rst",
      include_package_data=True,
      python_requires=">=3.6.0",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
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
