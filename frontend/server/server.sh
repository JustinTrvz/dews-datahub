#!/bin/bash

# Set the port
PORT=5000

# Stop any program currently running on the set port
echo 'Preparing port' $PORT '...'
fuser -k 5000/tcp

# switch directories
cd build/web/

# Start the server
echo 'Server for Flutter Web starting on port ' $PORT '...'
python3 -m http.server $PORT