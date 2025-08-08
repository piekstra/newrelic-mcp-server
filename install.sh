#!/bin/bash
# New Relic MCP Server Installation Script

set -e

echo "🚀 Installing New Relic MCP Server..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.7"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo "❌ Python 3.7+ is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make executable
echo "🔧 Making server executable..."
chmod +x newrelic_mcp_server.py

# Test basic functionality
echo "🧪 Testing installation..."
if python3 -c "import fastmcp, httpx; print('✅ Dependencies OK')"; then
    echo "🎉 Installation successful!"
    echo ""
    echo "Next steps:"
    echo "1. Set your environment variables:"
    echo "   export NEWRELIC_API_KEY='your-api-key'"
    echo "   export NEWRELIC_REGION='US'  # or 'EU'"
    echo "   export NEWRELIC_ACCOUNT_ID='your-account-id'"
    echo ""
    echo "2. Add to Claude Desktop config:"
    echo "   \"command\": \"python3\","
    echo "   \"args\": [\"$(pwd)/newrelic_mcp_server.py\"]"
    echo ""
    echo "3. Test the server:"
    echo "   ./newrelic_mcp_server.py"
else
    echo "❌ Installation test failed. Please check the error above."
    exit 1
fi
