#!/bin/bash

# Enable job control
set -m 

# Trap SIGINT and SIGTERM to clean up all child processes
# Syntax: trap 'commands' SIGNALS. 
# kill 0: Kill all processes in the current subprocess group
# SIGINT: When we press ctrl+c
# SIGTERM: Termination signal to gracefully stop a process
trap "kill 0" SIGINT SIGTERM

# Get the current directory of the project
PROJECT_ROOT=$(dirname "$PWD")
echo $PROJECT_ROOT

# Create a build directory in the project root if it doesn't exist
BUILD_DIR="$PROJECT_ROOT/build"
echo $BUILD_DIR
if [ ! -d "$BUILD_DIR" ]; then
  mkdir "$BUILD_DIR"
fi

cd $BUILD_DIR

# Configure with cmake
cmake ..

# Build project
make

EXECUTABLE="$BUILD_DIR/bme280_cpp_driver_executable"

# Check if the executable exists before running
if [ -f "$EXECUTABLE" ]; then
    # Run the C++ executable
    "$EXECUTABLE" &
else
    echo "Error: Executable not found at $EXECUTABLE"
fi

# Start the Python script that logs temperature data to the database
cd $PROJECT_ROOT
python3 src/main.py &

# Start the Flask web app
python3 src/flask_web_app.py

# Wait for all child processes
wait