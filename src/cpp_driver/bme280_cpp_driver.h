#ifndef BME280_CPP_DRIVER_H
#define BME280_CPP_DRIVER_H

#include <cstdint> // For uint_8_t ...
#include <sstream> // For std::ostringstream

// BME280 default I2C address
#define BME280_ADDRESS 0x77

// BME280 Registers
#define BME280_REG_TEMP_MSB 0xFA
#define BME280_REG_TEMP_LSB 0xFB
#define BME280_REG_TEMP_XLSB 0xFC
#define BME280_REG_CTRL_HUM 0xF2
#define BME280_REG_CTRL_MEAS 0xF4
#define BME280_REG_CONFIG 0xF5

#define PIPE_NAME "/tmp/sensor_pipe"  // Path for the named pipe

class BME280
{
public:
    BME280(const char* i2cDevice, uint8_t address);
    bool begin();
    float readTemperature();

private:
    int i2cFile; // File descriptor
    uint8_t i2cAddress;
    int32_t readRawTemperature();

    // Helper functions
    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);
    uint16_t read16(uint8_t reg);
    uint32_t read20(uint8_t reg);
    float compensateTemperature(int32_t rawTemp);
};


#endif