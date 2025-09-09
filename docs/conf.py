
# Sphinx configuration for TPM Job Finder POC
import os
import sys

project = 'TPM Job Finder POC'
author = 'Kevin Toles'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'

# Paths for autodoc
sys.path.insert(0, os.path.abspath('..'))  # Add workspace root
sys.path.insert(0, os.path.abspath('../src'))  # Add src folder
