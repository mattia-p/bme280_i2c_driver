#include <iostream> // cin, cout, cerr
#include <fcntl.h> // File control operations, open...
#include <unistd.h> // Work with files and hardware devices (read, write, close)
#include <sys/ioctl.h> // ioctl, IO control
#include <linux/i2c-dev.h> // I2c 
#include <cstdint> // For uint_8_t ...

// BME280 default I2C address
#define BME280_ADDRESS 0x77

// BME280 Registers
#define BME280_REG_TEMP_MSB 0xFA
#define BME280_REG_TEMP_LSB 0xFB
#define BME280_REG_TEMP_XLSB 0xFC
#define BME280_REG_CTRL_HUM 0xF2
#define BME280_REG_CTRL_MEAS 0xF4
#define BME280_REG_CONFIG 0xF5

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

BME280::BME280(const char* i2cDevice, uint8_t address) : i2cAddress(address){
    
    // Open i2c bus
    i2cFile = open(i2cDevice, O_RDWR); // O_RDWR (open for reading and writing)
    if (i2cFile < 0)
    {
        std::cerr << "Failed to open the i2c bus \n";
        exit(1);
    }

    // Set the i2c slave address
    if (ioctl(i2cFile, I2C_SLAVE, i2cAddress) < 0) // I/O control. 
    {
        std::cerr << "Failed to acquire bus access or talk to the BME280\n";
        exit(1);
    }
}



bool BME280::begin(){
    // Configure the BME280 sensor
    writeRegister(BME280_REG_CTRL_HUM, 0x01);  // Humidity oversampling x1
    writeRegister(BME280_REG_CTRL_MEAS, 0x27); // Normal mode, oversampling x1 for temperature
    writeRegister(BME280_REG_CONFIG, 0xA0); // Set config (filter off, standby)


    return true;
}

float BME280::readTemperature(){
    // 
    int32_t rawTemp = readRawTemperature();

    // Compensate the temperature using the formula and calibration values
    
    return compensateTemperature(rawTemp);
}

int32_t BME280::readRawTemperature(){
    // The temperature is a 20-bit value spread accross 3 registers
    uint32_t rawTemp = read20(BME280_REG_TEMP_MSB);
    return rawTemp >> 4; // The least significant 4 bits are not part of the temperature
}

void BME280::writeRegister(uint8_t reg, uint8_t value){
    //
    uint8_t buffer[2] = {reg, value};
    if (write(i2cFile, buffer, 2) != 2){
        std::cerr << "Failed to write to the registers\n";
    }
}

float BME280::compensateTemperature(int32_t rawTemp){
    int32_t var1;
    int32_t var2;
    int32_t t_fine;

    uint16_t dig_T1 = read16(0x88);
    int16_t dig_T2 = (int16_t)read16(0x8A);
    int16_t dig_T3 = (int16_t)read16(0x8C);

    std::cout << "Calibration data: dig_T1 = " << dig_T1 
              << ", dig_T2 = " << dig_T2 << ", dig_T3 = " << dig_T3 << std::endl;

    // Compensation formula
    var1 = ((((rawTemp >> 3) - (dig_T1 << 1))) * dig_T2) >> 11;
    var2 = (((((rawTemp >> 4) - dig_T1) * ((rawTemp >> 4) - dig_T1)) >> 12) * dig_T3) >> 14;

    t_fine = var1 + var2;
    float temperature = (t_fine * 5 + 128) >> 8;

    return temperature / 100.0;
}

uint8_t BME280::readRegister(uint8_t reg){
    // reg: register address from which we want to read a byte

    if (write(i2cFile, &reg, 1) != 1){ // Sends the address of the register we want to read from to the sensor. 1: 1 byte
        // We need to write the register address to the i2c bus
        std::cerr << "Failed to write to the register\n";
    }

    uint8_t data;
    if (read(i2cFile, &data, 1) != 1){
        std::cerr << "Failed to read from the register\n";
    }

    return data;
}

uint16_t BME280::read16(uint8_t reg){
    // 
    uint8_t buffer[2];
    if (write(i2cFile, &reg, 1) != 1){
        std::cerr << "Failed to write to the register\n";
    }

    if (read(i2cFile, buffer, 2) != 2){
        std::cerr << "Failed to read from the register\n";
    }

    return (buffer[0] << 8 | buffer[1]);

}

uint32_t BME280::read20(uint8_t reg){
    uint8_t buffer[3];

    if (write(i2cFile, &reg, 1) != 1){
        std::cerr << "Failed to write to the register\n";
    }

    if (read(i2cFile, buffer, 3) != 3){
        std::cerr << "Failed to read from register\n";
    }

    return (buffer[0] << 16 | buffer[1] << 8 | buffer[2]);
}


int main()
{
    BME280 sensor("/dev/i2c-1", BME280_ADDRESS);

    if (!sensor.begin())
    {
        std::cerr << "Failed to initialize BME280\n";
        return 1;
    }

    // Read temperature
    float temperature = sensor.readTemperature();

    std::cout << "Temperature: " << temperature << " °C" << std::endl;


    return 0;
}