#!/bin/bash

# L{CORE} Frontend Setup Script
# Automates the installation and configuration process

set -e

echo "🚀 Setting up L{CORE} Frontend..."
echo ""

# Check Node.js version
NODE_VERSION=$(node --version 2>/dev/null || echo "not installed")
if [[ $NODE_VERSION == "not installed" ]]; then
    echo "❌ Node.js is not installed. Please install Node.js v20+ and try again."
    exit 1
fi

echo "✅ Node.js version: $NODE_VERSION"

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ package.json not found. Please run this script from the lcore-frontend directory."
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Copy environment template
if [[ ! -f ".env" ]]; then
    echo ""
    echo "📝 Creating environment file..."
    cp env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your WalletConnect Project ID"
    echo "   Get one from: https://cloud.walletconnect.com/"
    echo ""
else
    echo ""
    echo "✅ .env file already exists"
fi

# Generate GraphQL types (optional, will be done on first run anyway)
echo ""
echo "🔄 Generating GraphQL types..."
npm run codegen 2>/dev/null || echo "⚠️  GraphQL types will be generated on first run"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env file with your WalletConnect Project ID"
echo "  2. Run 'npm run dev' to start the development server"
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "🔗 Resources:"
echo "  • Documentation: README.md"
echo "  • Development Plan: L{CORE}_FRONTEND_DEVELOPMENT_PLAN.md"
echo "  • GraphQL Endpoint: https://lcore-iot-node-production.up.railway.app/graphql"
echo ""
echo "Happy coding! 🚀" 