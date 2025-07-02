VERSION=0.0.1

# if .env file exists VERSION, update it
if grep -q "VERSION=" ./.env; then
    sed -i '' "s/VERSION=.*/VERSION=$VERSION/" ./.env
else
    # if not exists, add to file end
    echo "" >> ./.env
    echo "VERSION=$VERSION" >> ./.env
fi