VERSION=0.0.1

# if .env file exists VERSION, update it
if grep -q "VERSION=" ./.env; then
    # Cross-platform sed command that works on both macOS and Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VERSION=.*/VERSION=$VERSION/" ./.env
    else
        # Linux
        sed -i "s/VERSION=.*/VERSION=$VERSION/" ./.env
    fi
else
    # if not exists, add to file end
    echo "" >> ./.env
    echo "VERSION=$VERSION" >> ./.env
fi