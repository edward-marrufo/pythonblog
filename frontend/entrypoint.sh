#!/bin/sh
#/frontend/entrypoint.sh
set -e # exit on error

cd /app

#if package.json doesn't exist then we create a new React app
if [ ! -f /app/package.json ]; then
    echo "No React application detected. Bootstrapping now!"
    npx --yes create-vite@latest . --template react
    echo "Installing dependencies"
    npm install
fi

#If node_modules is missing install the dependencies
if [ ! -d /app/node_modules ]; then
    echo "Installing dependencies"
    npm install
fi

#starting our React dev server
##cd /app
echo "Starting React server"
exec npm run dev -- --host 0.0.0.0