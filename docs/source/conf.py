# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'A2SQuery'
copyright = '2022, Liam (linKhehe) Henderson'
author = 'Liam (linKhehe) Henderson'

collapse_navigation = False

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "enum_tools.autoenum",
    "sphinx.ext.doctest"
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme_options = {
    "show_navbar_depth": 3,
    "home_page_in_toc": True
}

html_theme = 'sphinx_book_theme'
html_title = "A2SQuery"
