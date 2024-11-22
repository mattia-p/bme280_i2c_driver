#!/bin/bash

# Enable job control
set -m 

# Trap SIGINT and SIGTERM to clean up all child processes
# Syntax: trap 'commands' SIGNALS. 
# kill 0: Kill all processes in the current subprocess group
# SIGINT: When we press ctrl+c
# SIGTERM: Termination signal to gracefully stop a process
trap "kill 0" SIGINT SIGTERM

# Build files
bazel build //src/cpp_driver:bme280_cpp_driver
bazel build //src:main
bazel build //src:flask_web_app

# Build the cpp driver
# g++ -o ../src/cpp_driver/cpp_driver ../src/cpp_driver/bme280_cpp_driver.cpp
# bazel build //src/cpp_driver:bme280_cpp_driver

# Start the C++ driver in the background
# ./../src/cpp_driver/cpp_driver &
bazel run //src/cpp_driver:bme280_cpp_driver &
bazel run //src:main &
bazel run //src:flask_web_app



# Start the Python script that logs temperature data to the database
# python3 ../src/main.py &

# Start the Flask web app
# python3 ../src/flask_web_app.py

# Wait for all child processes
wait