cmake_minimum_required(VERSION 3.16)
project(BME280Sensor)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)

# Set the include directory for the cpp_driver library
include_directories(src/cpp_driver)

add_library(bme280_cpp_driver
    src/cpp_driver/bme280_cpp_driver.cpp
)

# Add the executable from main.cpp
add_executable(bme280_cpp_driver_executable
    src/cpp_driver/main.cpp
)

# Link the executable with the bme280_cpp_driver library
target_link_libraries(bme280_cpp_driver_executable bme280_cpp_driver)