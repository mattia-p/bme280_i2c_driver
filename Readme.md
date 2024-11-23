# BME280 driver

## Instructions

Scan the i2c bus to know the address of the devices connected to it. 
```bash
sudo i2cdetect -y 1
```

### Build

```bash
bazel build //src/cpp_driver:bme280_cpp_driver_executable
bazel build //src:main
bazel build //src:flask_web_app
```

### Start

Start the C++ i2c driver
```bash
bazel run //src/cpp_driver:bme280_cpp_driver_executable &
```

Start the python main file:
```bash
bazel run //src:main &
```

Start the flask app:
```bash
bazel run //src:flask_web_app
```

### Run and stop all scripts at the same time

To start all scripts at once:
```bash
./start.sh
```

Find PID of start.sh:
```bash
ps -a
```

To kill all child processes at once:
```bash
pkill -P < start_script_pid >
```

## Improvements
- Turn off sensor in between measurements?
- Measure power consumption?
- Error handling (sensor now found ...), app error...
- Formatting (clang...)
- CMake instead of g++
- Memory management/handling
- C++ version, separate data registers and calibration registers
- Pi mini with ubuntu server?
- Add humidity and pressure
- Add tests
- Handle UTC time in database
- Add logging and remove print statements
- Add diagram
- Handle db memory?
- Autocomplete

## Result example

![](assets/temperature_app.png)