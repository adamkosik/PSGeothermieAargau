# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
import pyvista
import numpy as np

pyvista.set_error_output_file('errors.txt')
# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True
# Preferred plotting style for documentation
pyvista.set_plot_theme('document')
pyvista.rcParams['window_size'] = np.array([1024, 768]) * 2
# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath('./images/'), 'auto-generated/')
pyvista.BUILDING_GALLERY = True
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

from sphinx_gallery.sorting import FileNameSortKey, ExplicitOrder

# -- Project information -----------------------------------------------------
year = datetime.date.today().year
project = 'Pilot Study Geothermie Aargau'
copyright = f'2019 - {year}, Jan Niederau'
author = 'Jan Niederau'

# The full version, including alpha/beta/rc tags
release = 'ALPHA'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx_gallery.gen_gallery',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages'
    ]
# 'hachibee_sphinx_theme'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#import hachibee_sphinx_theme
#html_theme_path = [hachibee_sphinx_theme.get_html_themes_path()]
#html_theme = 'haiku'
html_theme = 'alabaster'
html_logo = './_static/logos/ps_aargau_logo_200px.png'
pygments_style = 'sphinx'
# 'hachibee'
# 'sphinx_rtd_theme'
# 'alabaster'
html_theme_options = {
    'github_user': 'Japhiolite',
    'github_repo': 'PSGeothermieAargau',
    'logo_name': False,
    'travis_button': False,
    'page_width': '1200px',
    'fixed_sidebar': False,
    'show_related': True,
   'sidebar_collapse': True,
 }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# sphinx-gallery configuration
sphinx_gallery_conf = {
    # path to your example scripts
    'examples_dirs': [
        '../../examples/Examples',
        '../../examples/Tutorials'],
    # path to where to save gallery generated output
    'gallery_dirs': [
        'Examples',
        'Tutorials'],
    #'subsection_order': ExplicitOrder(['../../examples/WP1-data_analysis',
    #                                    '../../examples/WP2-geo_modeling',
    #                                    '../../examples/WP3-heat_transport']),
    # Patter to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # specify that examples should be ordered according to filename
    'within_subsection_order': FileNameSortKey,
    # directory where function granular galleries are stored
    'backreferences_dir': 'gen_modules/backreferences',
    # Modules for which function level galleries are created.  In
    # this case sphinx_gallery and numpy in a tuple of strings.
    'doc_module': ('OpenWF', 'gempy', 'numpy', 'pandas', 'matplotlib'),
    'pypandoc': False,
    'image_scrapers': ('matplotlib', 'pyvista'),
    'first_notebook_cell': ("%matplotlib inline\n"
                            "from pyvista import set_plot_theme\n"
                            "set_plot_theme('document')")
}

# configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/{.major}'.format(sys.version_info), None),
    'matplotlib': ('https://matplotlib.org/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable', None),
    'skimage': ('https://scikit-image.org/docs/dev/', None),
    'pyvista': ('https://docs.pyvista.org/', None),
    'sphinx': ('http://www.sphinx-doc.org/en/stable', None),
    'sqlite3': ('https://docs.python.org/3/library/sqlite3.html', None)
}
