# API Documentation

This directory contains the reStructuredText (.rst) files for Sphinx API documentation.

## Building the Documentation

### Install Requirements

```bash
pip install -r requirements-dev.txt
```

Or install Sphinx manually:

```bash
pip install sphinx sphinx-rtd-theme myst-parser
```

### Build HTML Documentation

```bash
# Navigate to docs directory
cd docs

# Build HTML documentation
make html

# Or on Windows:
make.bat html
```

The generated documentation will be in `docs/_build/html/`.

### View Documentation

Open `docs/_build/html/index.html` in your browser:

```bash
# Linux/Mac
open _build/html/index.html

# Windows
start _build/html/index.html
```

### Live Preview (Auto-rebuild)

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live server
make livehtml
```

Then visit `http://127.0.0.1:8000` in your browser.

### Clean Build

```bash
make clean
make html
```

## Adding New API Documentation

To add documentation for a new module:

1. Create a new `.rst` file in this directory (e.g., `newmodule.rst`)
2. Add the module reference:

```rst
NewModule
=========

.. automodule:: mymt5.newmodule
   :members:
   :undoc-members:
   :show-inheritance:
```

3. Add the file to `docs/index.rst` in the appropriate toctree:

```rst
.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/account
   api/newmodule
```

4. Rebuild the documentation:

```bash
make html
```

## Documentation Style

- Use Google-style docstrings in Python code
- Include examples in docstrings where appropriate
- Document all public methods, classes, and functions
- Include type hints for better documentation

Example:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description with more details about what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails
    
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Available Build Formats

Sphinx can generate documentation in multiple formats:

- `make html` - HTML documentation (default)
- `make pdf` - PDF documentation (requires LaTeX)
- `make epub` - EPUB ebook format
- `make man` - Unix manual pages
- `make text` - Plain text
- `make linkcheck` - Check all links

## Publishing Documentation

### GitHub Pages

1. Build the documentation:
```bash
make html
```

2. Create `.nojekyll` file:
```bash
touch _build/html/.nojekyll
```

3. Commit and push to GitHub:
```bash
git add _build/html
git commit -m "Update documentation"
git push origin main
```

4. Enable GitHub Pages in repository settings

### Read the Docs

1. Create account on [readthedocs.org](https://readthedocs.org)
2. Import your GitHub repository
3. Configure build settings
4. Documentation will auto-build on each commit

## Troubleshooting

### Module Import Errors

If Sphinx can't import modules, ensure:

1. Package is installed: `pip install -e .`
2. Virtual environment is activated
3. Python path is correct in `docs/conf.py`

### Missing Dependencies

```bash
pip install -r requirements-dev.txt
```

### Build Warnings

Fix all warnings before publishing:

```bash
make html SPHINXOPTS="-W"
```

This treats warnings as errors.

## More Information

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html)

