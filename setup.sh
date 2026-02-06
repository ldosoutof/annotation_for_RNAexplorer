#!/bin/bash

# Annotation for RNAexplorer - Setup Script
# This script automates the installation and setup process

set -e  # Exit on error

echo "=========================================="
echo "Annotation for RNAexplorer - Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check pip
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (recommended) [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Make scripts executable
echo "Making scripts executable..."
chmod +x rnaseq_analysis.py
chmod +x scripts/*.py
chmod +x test_pipeline.py
echo -e "${GREEN}✓ Scripts are now executable${NC}"

# Create example samples file
if [ ! -f "samples.txt" ]; then
    echo "Creating example samples.txt..."
    cp samples_example.txt samples.txt
    echo -e "${GREEN}✓ Example samples.txt created${NC}"
else
    echo -e "${YELLOW}⚠ samples.txt already exists, skipping${NC}"
fi

# Test installation
echo ""
echo "Testing installation..."
if python3 test_pipeline.py; then
    echo -e "${GREEN}✓ Installation test passed!${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    echo "Please check the error messages above"
    exit 1
fi

# Create directories
echo "Creating output directories..."
mkdir -p results
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit samples.txt with your sample IDs"
echo "2. Run: python rnaseq_analysis.py --help"
echo "3. See QUICKSTART.md for usage examples"
echo ""

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Note: Virtual environment is activated."
    echo "To activate it later, run: source venv/bin/activate"
fi

echo ""
echo "Happy analyzing! 🧬"
