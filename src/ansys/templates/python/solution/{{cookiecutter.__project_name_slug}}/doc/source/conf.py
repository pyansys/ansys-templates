# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Sphinx documentation configuration file."""


from datetime import datetime
import os
from pathlib import Path

from ansys_sphinx_theme import ansys_favicon, get_version_match
import toml

BRANCH = "main"
ORGANIZATION_NAME = "ansys-internal"
DOC_PATH = "doc/source"


def remove_scheme_from_url(url: str) -> tuple:
    """Remove the scheme part of a URL."""
    items = url.split("://")
    if len(items) == 2:
        return items[0], items[1]
    else:
        raise Exception(f"Fail to return the URL without the scheme part for {url}.")


def get_repository_name_from_url(url: str) -> str:
    """Get repository name from the URL."""
    repository_name = remove_scheme_from_url(repository_url)[1].split("/")[-1]
    if ".git" in repository_name:
        repository_name = repository_name.split(".git")[0]
    return repository_name


# ---------- // Project Information // --------------------------------------------------------------------------------

configuration_file = Path(__file__).parent.parent.parent.absolute() / "pyproject.toml"
if configuration_file.exists():
    configuration = toml.load(configuration_file)
else:
    raise FileNotFoundError("No configuration file at project's root.")

project_name = configuration.get("tool", {}).get("poetry", {}).get("name", None)
package_version = configuration.get("tool", {}).get("poetry", {}).get("version", None)
documentation_url = configuration.get("tool", {}).get("poetry", {}).get("documentation", None)
repository_url = configuration.get("tool", {}).get("poetry", {}).get("repository", None)

if documentation_url:
    cname = remove_scheme_from_url(documentation_url)[1]
else:
    cname = None

if documentation_url:
    repository_name = remove_scheme_from_url(repository_url)
else:
    repository_name = None

copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."
switcher_version = get_version_match(package_version)


# ---------- // General configuration // ------------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_code_tabs",
    "sphinx.ext.todo",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_design",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
}

# pydantic configuration
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config = False
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_validator_summary = False

suppress_warnings = ["label.*"]

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Favicon
html_favicon = ansys_favicon

# notfound.extension
notfound_template = "404.rst"
notfound_urls_prefix = "/../"

# static path
html_static_path = ["_static"]

html_css_files = ['css/custom.css']

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "links.rst",
    "substitutions.rst",
]

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

autodoc_mock_imports = ["ansys.platform", "opentelemetry"]
numfig = True
numfig_secnum_depth = 1
numfig_format = {
    "figure": "Figure %s ",
    "table": "Table %s ",
    "code-block": "Code sample %s ",
}

# ---------- // Copy button customization // --------------------------------------------------------------------------

# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True


# ---------- // Sphinx Gallery Options // -----------------------------------------------------------------------------


# ---------- // Options for HTML output // ----------------------------------------------------------------------------

html_short_title = html_title = "Ansys Solutions {{cookiecutter.__solution_display_name}}"
html_theme = "ansys_sphinx_theme"
html_logo = str(Path(__file__).parent.absolute() / "_static" / "ansys-solutions-logo-black-background.png")
html_theme_options = {
    "logo": "ansys",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": False,
    "additional_breadcrumbs": [
        ("Ansys Internal", "https://github.com/ansys-internal"),
     ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
}

if str(os.getenv("DISABLE_GITHUB_URL_LINK")).lower() != "true":
    html_theme_options["github_url"] = f"https://github.com/{ORGANIZATION_NAME}/{repository_name}"

html_context = {
    "display_github": False,  # Integrate GitHub
    "github_user": ORGANIZATION_NAME,
    "github_repo": repository_name,
    "github_version": BRANCH,
    "doc_path": DOC_PATH,
    "default_mode": "dark"
}
html_show_sourcelink = False
html_compact_lists = False


# ---------- // Options for HTMLHelp output // ------------------------------------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "ansys-solutions-{{cookiecutter.__project_name_slug}}-documentation"


# ---------- // Options for LaTeX output // ---------------------------------------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"Ansys-Solutions-{{cookiecutter.__project_name_slug}}-Documentation-{package_version}.tex",
        "Ansys Solutions {{cookiecutter.__solution_display_name}} Documentation",
        author,
        "manual",
    ),
]


# ---------- // [Options for manual page output // --------------------------------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        "Ansys Solutions {{cookiecutter.__solution_display_name}}",
        "Ansys Solutions {{cookiecutter.__solution_display_name}} Documentation",
        [author],
        1,
    )
]


# ---------- // Options for Texinfo output // -------------------------------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "Ansys Solutions {{cookiecutter.__solution_display_name}}",
        "Ansys Solutions {{cookiecutter.__solution_display_name}} Documentation",
        author,
        "Ansys Solutions {{cookiecutter.__solution_display_name}}",
        "Engineering Software",
    ),
]

# Keep these while the repository is private
linkcheck_ignore = [
    "{{ cookiecutter.__repository_url }}/*",
    {%- if cookiecutter.__template_name == "pyansys-advanced" %}
    "{{ cookiecutter.__documentation_url }}/version/stable/*",
    {%- endif %}
    "https://pypi.org/project/{{cookiecutter.__pkg_name}}",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(f"https://github.com/ansys/{{ cookiecutter.__pkg_namespace }}/releases/tag/v{package_version}")
