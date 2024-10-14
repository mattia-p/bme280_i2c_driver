# BME280 driver

## Improvements

- Turn off sensor in between measurements?
- Measure power consumption?
- c++ driver
- IPC driver <> rest of app
- Error handling (sensor now found ...)
- Formatting (clang...)
- CMake
- Memory management/handling
- C++ version, separate data registers and calibration registers
- Pi mini with ubuntu server?
- Add humidity and pressure
- Add tests

## Instructions

Scan the i2c bus to know the address of the devices connected to it. 
```bash
sudo i2cdetect -y 1
```

## Build

```bash
g++ -o cpp_driver bme280_cpp_driver.cpp
```