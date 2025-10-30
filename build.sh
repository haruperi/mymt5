#!/bin/bash
# MyMT5 Build Script for Linux/Mac

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║                  MyMT5 BUILD SCRIPT                      ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Clean
echo -e "${YELLOW}[1/5] Cleaning old builds...${NC}"
rm -rf build/ dist/ *.egg-info
echo -e "${GREEN}✓ Clean complete${NC}"
echo ""

# Step 2: Check tools
echo -e "${YELLOW}[2/5] Checking build tools...${NC}"
python -m pip install --upgrade pip setuptools wheel build twine --quiet
echo -e "${GREEN}✓ Build tools ready${NC}"
echo ""

# Step 3: Build
echo -e "${YELLOW}[3/5] Building package...${NC}"
python -m build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 4: Check
echo -e "${YELLOW}[4/5] Checking package...${NC}"
twine check dist/*
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Package check passed${NC}"
else
    echo -e "${RED}✗ Package check failed${NC}"
    exit 1
fi
echo ""

# Step 5: List artifacts
echo -e "${YELLOW}[5/5] Build artifacts:${NC}"
ls -lh dist/
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║              BUILD COMPLETE!                             ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  • Test: pip install dist/mymt5-1.0.0-py3-none-any.whl"
echo "  • Upload to Test PyPI: twine upload --repository testpypi dist/*"
echo "  • Upload to PyPI: twine upload dist/*"



