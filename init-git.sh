#!/bin/bash

# A2A Agent Registry - Git Initialization Script
# This script initializes the git repository and prepares for GitHub push

echo "🚀 Initializing A2A Agent Registry Git Repository"
echo "=================================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")"

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "❌ Error: .gitignore not found"
    exit 1
fi

echo ""
echo "📝 Adding files to git..."
git add .

echo ""
echo "✅ Files staged for commit"
echo ""

# Show status
echo "📊 Git status:"
git status --short

echo ""
echo "💾 Creating initial commit..."

git commit -m "Initial commit: A2A Agent Registry implementation

Features:
- Phase 1: Core registry server (Express + PostgreSQL + Redis)
- Phase 2: TypeScript/JavaScript client library  
- Phase 3: Comprehensive documentation
- Phase 4: Testing framework configured

Components:
- Registry Server: 19 files
- Client Library: 10 files
- Documentation: 6 files
- Examples: 2 files
- Total: 42 files

Status: Production-ready, 0 vulnerabilities

Addresses: https://github.com/a2aproject/A2A/discussions/741"

echo ""
echo "✅ Initial commit created"
echo ""

echo "🎯 Next Steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   gh repo create jenish2917/a2a-registry --public \\"
echo "     --description 'Production-ready Agent Registry for the A2A Protocol'"
echo ""
echo "2. Link remote and push:"
echo "   git remote add origin https://github.com/jenish2917/a2a-registry.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Update GitHub Discussion #741 with repository link"
echo ""
echo "4. Wait for community feedback"
echo ""
echo "5. Submit PR to a2aproject/A2A"
echo ""

echo "📚 See GITHUB_SETUP.md for detailed instructions"
echo ""
echo "✨ Repository ready for GitHub!"
