#!/bin/bash

# Script d'Intégration Git Automatique
# Configure et pousse le pipeline vers GitHub

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Annotation for RNAexplorer - Git Integration"
echo -e "==========================================${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed${NC}"
    echo "Install it with: sudo apt install git"
    exit 1
fi

# Check if we're already in a git repository
if [ -d .git ]; then
    echo -e "${YELLOW}⚠ This directory is already a Git repository${NC}"
    read -p "Do you want to continue? This will reset the repository. [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    rm -rf .git
fi

# Get user information
echo -e "${BLUE}Step 1: Git Configuration${NC}"
echo "------------------------"

# Check if git user is configured
GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
    echo "Git user not configured. Let's set it up."
    
    read -p "Enter your name: " USER_NAME
    read -p "Enter your email: " USER_EMAIL
    
    git config --global user.name "$USER_NAME"
    git config --global user.email "$USER_EMAIL"
    
    echo -e "${GREEN}✓ Git user configured${NC}"
else
    echo -e "Current Git user: ${GREEN}$GIT_USER <$GIT_EMAIL>${NC}"
fi

echo ""

# Get repository information
echo -e "${BLUE}Step 2: Repository Information${NC}"
echo "------------------------------"

read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter repository name [annotation_for_RNAexplorer]: " REPO_NAME
REPO_NAME=${REPO_NAME:-annotation_for_RNAexplorer}

echo ""
echo -e "${YELLOW}Note: Make sure you've created the repository on GitHub:${NC}"
echo -e "  https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
read -p "Have you created the repository on GitHub? [y/N] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Please create the repository on GitHub first:${NC}"
    echo "  1. Go to https://github.com/new"
    echo "  2. Repository name: $REPO_NAME"
    echo "  3. Description: RNA-Seq analysis pipeline for FRASER2 and OUTRIDER"
    echo "  4. DO NOT initialize with README (we have files already)"
    echo "  5. Click 'Create repository'"
    echo ""
    read -p "Press Enter when done..."
fi

echo ""
echo -e "${BLUE}Step 3: Initialize Git Repository${NC}"
echo "----------------------------------"

# Initialize git
git init
echo -e "${GREEN}✓ Git repository initialized${NC}"

# Create .gitattributes for consistent line endings
cat > .gitattributes << 'EOF'
# Auto detect text files and perform LF normalization
* text=auto

# Python
*.py text eol=lf

# Shell scripts
*.sh text eol=lf

# Markdown
*.md text eol=lf

# YAML
*.yaml text eol=lf
*.yml text eol=lf

# Data files (don't normalize)
*.tsv binary
*.tab binary
*.gtf binary
EOF

echo -e "${GREEN}✓ Created .gitattributes${NC}"

# Add all files
echo ""
echo -e "${BLUE}Step 4: Stage Files${NC}"
echo "-------------------"

git add .
echo -e "${GREEN}✓ All files staged${NC}"

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -20
FILE_COUNT=$(git status --short | wc -l)
echo "... ($FILE_COUNT files total)"

echo ""
read -p "Continue with commit? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Create initial commit
echo ""
echo -e "${BLUE}Step 5: Create Initial Commit${NC}"
echo "------------------------------"

git commit -m "Initial commit: Annotation for RNAexplorer

Pipeline d'annotation pour FRASER2 et OUTRIDER avec support RNAexplorer.

Features:
- FRASER2 and OUTRIDER annotation
- GTF annotation integration
- PanelApp and gnomAD support
- ZIP file auto-detection with interactive mode
- Variant filtering and prioritization
- TSV export
- Comprehensive documentation

Structure:
- Main pipeline: rnaseq_analysis.py
- ZIP analyzer: analyze_from_zip.py
- Utilities: scripts/
- Documentation: *.md files
- Tests: test_pipeline.py"

echo -e "${GREEN}✓ Initial commit created${NC}"

# Add remote
echo ""
echo -e "${BLUE}Step 6: Add Remote Repository${NC}"
echo "------------------------------"

REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
git remote add origin "$REMOTE_URL"
echo -e "${GREEN}✓ Remote added: $REMOTE_URL${NC}"

# Set main branch
git branch -M main

# Push to GitHub
echo ""
echo -e "${BLUE}Step 7: Push to GitHub${NC}"
echo "----------------------"

echo "Pushing to GitHub..."
echo "(You may be asked for your GitHub credentials)"
echo ""

if git push -u origin main; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✓ Successfully pushed to GitHub!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Your repository is now available at:"
    echo -e "${BLUE}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository on GitHub"
    echo "  2. Add a description and topics"
    echo "  3. Create a release: GitHub > Releases > Create new release"
    echo "  4. Consider adding:"
    echo "     - GitHub Actions for CI/CD"
    echo "     - Issue templates"
    echo "     - Wiki documentation"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Push failed${NC}"
    echo ""
    echo "Common issues:"
    echo "  1. Repository doesn't exist on GitHub"
    echo "  2. Authentication failed (check credentials)"
    echo "  3. Repository already has content (if so, use force push cautiously)"
    echo ""
    echo "To retry manually:"
    echo "  git push -u origin main"
    echo ""
    echo "For authentication issues, consider using SSH:"
    echo "  git remote set-url origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
    echo ""
    exit 1
fi

# Optional: Create initial tag
echo ""
read -p "Do you want to create an initial release tag (v1.0.0)? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    git tag -a v1.0.0 -m "First stable release

Features:
- Complete FRASER2/OUTRIDER processing pipeline
- ZIP auto-detection
- Comprehensive annotation support
- Full documentation"
    
    git push origin v1.0.0
    echo -e "${GREEN}✓ Tag v1.0.0 created and pushed${NC}"
    echo ""
    echo "Create a release on GitHub:"
    echo "  https://github.com/$GITHUB_USER/$REPO_NAME/releases/new?tag=v1.0.0"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete! 🎉"
echo -e "==========================================${NC}"
echo ""
echo "Useful Git commands:"
echo "  git status              - Check repository status"
echo "  git log --oneline       - View commit history"
echo "  git add <file>          - Stage files"
echo "  git commit -m 'msg'     - Commit changes"
echo "  git push                - Push to GitHub"
echo "  git pull                - Pull from GitHub"
echo ""
echo "Documentation:"
echo "  - See GIT_INTEGRATION.md for detailed Git usage"
echo "  - See README.md for pipeline documentation"
echo ""
