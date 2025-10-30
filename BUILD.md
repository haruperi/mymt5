# Building and Distributing MyMT5

This guide explains how to build, test, and distribute the MyMT5 package.

## Prerequisites

```bash
# Install build tools
pip install --upgrade pip setuptools wheel build twine
```

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info
# Windows:
# rmdir /s /q build dist
# del /q *.egg-info
```

### 2. Build Source Distribution and Wheel

```bash
# Using build (recommended)
python -m build

# Or using setup.py
python setup.py sdist bdist_wheel
```

This creates:
- `dist/mymt5-1.0.0.tar.gz` - Source distribution
- `dist/mymt5-1.0.0-py3-none-any.whl` - Wheel distribution

### 3. Verify the Build

```bash
# Check the contents
tar -tzf dist/mymt5-1.0.0.tar.gz | head -20
unzip -l dist/mymt5-1.0.0-py3-none-any.whl | head -20

# Check with twine
twine check dist/*
```

## Testing the Package

### 1. Test in a Clean Virtual Environment

```bash
# Create test environment
python -m venv test_env

# Activate it
# Windows:
test_env\Scripts\activate
# Linux/Mac:
source test_env/bin/activate

# Install from wheel
pip install dist/mymt5-1.0.0-py3-none-any.whl

# Test import
python -c "from mymt5 import MT5Client; print('Success!')"

# Test version
python -c "import mymt5; print(mymt5.__version__)"

# Deactivate and remove
deactivate
rm -rf test_env
```

### 2. Test Installation from Source

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install from source distribution
pip install dist/mymt5-1.0.0.tar.gz

# Test
python -c "from mymt5 import MT5Client; print('Success!')"

# Cleanup
deactivate
rm -rf test_env
```

## Uploading to PyPI

### 1. Test PyPI (Recommended First)

```bash
# Create account on test.pypi.org first

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mymt5
```

### 2. Production PyPI

```bash
# Create account on pypi.org first

# Upload to PyPI
twine upload dist/*

# Test installation
pip install mymt5
```

### 3. Using API Tokens (Recommended)

Create a `.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

## Automated Build Script

Create `build.sh` (Linux/Mac) or `build.bat` (Windows):

```bash
#!/bin/bash
# build.sh

echo "=== MyMT5 Build Script ==="

# Clean
echo "Cleaning old builds..."
rm -rf build/ dist/ *.egg-info

# Build
echo "Building package..."
python -m build

# Check
echo "Checking package..."
twine check dist/*

# List
echo "Build artifacts:"
ls -lh dist/

echo "=== Build complete ==="
```

Make it executable:
```bash
chmod +x build.sh
./build.sh
```

## Version Management

To release a new version:

1. Update version in `mymt5/__version__.py`:
```python
__version__ = '1.0.1'
```

2. Update `CHANGELOG.md`

3. Commit changes:
```bash
git add mymt5/__version__.py CHANGELOG.md
git commit -m "Release v1.0.1"
git tag v1.0.1
git push origin main --tags
```

4. Build and upload:
```bash
./build.sh
twine upload dist/*
```

## Troubleshooting

### Build Fails

```bash
# Update build tools
pip install --upgrade pip setuptools wheel build

# Check setup.py
python setup.py check

# Verbose build
python -m build --verbose
```

### Import Errors After Installation

```bash
# Check package contents
pip show mymt5
pip show -f mymt5

# Reinstall
pip uninstall mymt5
pip install mymt5 --no-cache-dir
```

### Missing Files in Distribution

Check `MANIFEST.in` and ensure all necessary files are included.

```bash
# Check what's included
python setup.py sdist
tar -tzf dist/mymt5-1.0.0.tar.gz
```

## Continuous Integration

Example GitHub Actions workflow (`.github/workflows/build.yml`):

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip setuptools wheel build twine
          pip install -e .[dev]
      
      - name: Run tests
        run: pytest tests/
      
      - name: Build package
        run: python -m build
      
      - name: Check package
        run: twine check dist/*
```

## Best Practices

1. **Always test in a clean environment** before uploading
2. **Use Test PyPI first** for new releases
3. **Use semantic versioning** (MAJOR.MINOR.PATCH)
4. **Update CHANGELOG.md** for each release
5. **Tag releases in git** with version numbers
6. **Sign releases** with GPG keys (optional but recommended)
7. **Keep build tools updated**

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Upload Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

**Ready to build?** Run `./build.sh` or follow the steps above!


