# Extract version from template/__init__.py
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION=$(grep '__version__ = "' $CURRENT_DIR/../template/__init__.py | sed 's/.*__version__ = "\([^"]*\)".*/\1/' | tr -d '\n')

# if .env file exists VERSION, update it
if grep -q "VERSION=" $CURRENT_DIR/../.env; then
    # Cross-platform sed command that works on both macOS and Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VERSION=.*/VERSION=$VERSION/" $CURRENT_DIR/../.env
    else
        # Linux
        sed -i "s/VERSION=.*/VERSION=$VERSION/" $CURRENT_DIR/../.env
    fi
else
    # if not exists, add to file end
    echo "" >> $CURRENT_DIR/../.env
    echo "VERSION=$VERSION" >> $CURRENT_DIR/../.env
fi