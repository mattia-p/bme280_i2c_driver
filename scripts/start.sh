#!/bin/bash

# Build the cpp driver
g++ -o ../src/cpp_driver/cpp_driver ../src/cpp_driver/bme280_cpp_driver.cpp

# Start the C++ driver in the background
./../src/cpp_driver/cpp_driver &

# Start the Python script that logs temperature data to the database
python3 ../src/main.py &

# Start the Flask web app
python3 ../src/flask_web_app.py