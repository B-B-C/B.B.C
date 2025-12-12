#!/bin/bash

# Load testing script for Django Forum

echo "Starting load tests..."

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "k6 is not installed. Installing..."
    # Install k6 (Linux/macOS)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install k6
    else
        echo "Please install k6 manually from https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
fi

# Start Django server in background
echo "Starting Django server..."
python manage.py runserver 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Run load tests
echo "Running load tests..."
k6 run load_tests/forum_load_test.js

# Stop Django server
echo "Stopping Django server..."
kill $SERVER_PID

echo "Load tests completed!"




