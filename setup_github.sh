#!/bin/bash
# Setup script for initializing and pushing the Kalshi Odds Comparison project to GitHub

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Kalshi Odds Comparison project for GitHub${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install Git first.${NC}"
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo -e "${BLUE}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized${NC}"
else
    echo -e "${BLUE}Git repository already initialized${NC}"
fi

# Create initial structure
echo -e "${BLUE}Creating project structure...${NC}"
mkdir -p src/data_collection src/analysis src/utils tests

# Create __init__.py files
touch src/__init__.py
touch src/data_collection/__init__.py
touch src/analysis/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# Stage all files
echo -e "${BLUE}Staging files for commit...${NC}"
git add .

# Initial commit
echo -e "${BLUE}Creating initial commit...${NC}"
git commit -m "Initial project structure for Kalshi Odds Comparison"

# Get GitHub repository URL
echo -e "${BLUE}Please create a new GitHub repository and enter the URL below:${NC}"
read -p "GitHub repository URL: " github_url

if [ -z "$github_url" ]; then
    echo -e "${RED}No GitHub URL provided. Skipping remote setup.${NC}"
    echo -e "${BLUE}You can manually set up the remote later with:${NC}"
    echo "  git remote add origin YOUR_GITHUB_URL"
    echo "  git branch -M main"
    echo "  git push -u origin main"
else
    # Add GitHub remote
    echo -e "${BLUE}Adding GitHub remote...${NC}"
    git remote add origin $github_url
    
    # Rename branch to main if it's not already
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        echo -e "${BLUE}Renaming current branch to main...${NC}"
        git branch -M main
    fi
    
    # Push to GitHub
    echo -e "${BLUE}Pushing to GitHub...${NC}"
    git push -u origin main
    
    echo -e "${GREEN}Successfully pushed to GitHub!${NC}"
    echo -e "${BLUE}Repository URL: ${NC}$github_url"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Complete the implementation of the missing components"
echo "2. Configure your config.yaml file with API credentials"
echo "3. Run the application with: python -m src.main"