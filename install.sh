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
MIN_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Python 3.10+ is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Install the package
echo "📦 Installing New Relic MCP Server..."
pip3 install -e .

# Test basic functionality
echo "🧪 Testing installation..."
if python3 -c "import fastmcp, httpx, keyring; print('✅ Dependencies OK')"; then
    echo "🎉 Installation successful!"
    echo ""
    echo "🔐 SECURE SETUP (Recommended for macOS):"
    echo "1. Run the secure credential setup:"
    echo "   newrelic-mcp-setup"
    echo ""
    echo "2. Add to Claude Desktop config (secure version):"
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"newrelic\": {"
    echo "         \"command\": \"newrelic-mcp-server\","
    echo "         \"env\": {"
    echo "           \"NEWRELIC_REGION\": \"US\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "📋 ALTERNATIVE (Environment Variables):"
    echo "1. Set your environment variables:"
    echo "   export NEWRELIC_API_KEY='your-api-key'"
    echo "   export NEWRELIC_REGION='US'  # or 'EU'"
    echo "   export NEWRELIC_ACCOUNT_ID='your-account-id'"
    echo ""
    echo "2. Add to Claude Desktop config:"
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"newrelic\": {"
    echo "         \"command\": \"newrelic-mcp-server\","
    echo "         \"env\": {"
    echo "           \"NEWRELIC_API_KEY\": \"your-api-key\","
    echo "           \"NEWRELIC_REGION\": \"US\","
    echo "           \"NEWRELIC_ACCOUNT_ID\": \"your-account-id\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "🚀 Test the server:"
    echo "   newrelic-mcp-server --help"
else
    echo "❌ Installation test failed. Please check the error above."
    exit 1
fi
