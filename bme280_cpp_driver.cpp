#include <iostream> // cin, cout, cerr
#include <fcntl.h> // File control operations, open...
#include <unistd.h> // Work with files and hardware devices (read, write, close)
#include <sys/ioctl.h> // ioctl, IO control
#include <linux/i2c-dev.h> // I2c 
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
    std::cout << "Open I2C bus" << std::endl;
    i2cFile = open(i2cDevice, O_RDWR); // O_RDWR (open for reading and writing)
    if (i2cFile < 0)
    {
        std::cerr << "Failed to open the i2c bus \n";
        exit(1);
    }

    // Set the i2c slave address
    std::cout << "Set i2c slave address" << std::endl;
    if (ioctl(i2cFile, I2C_SLAVE, i2cAddress) < 0) // I/O control. 
    {
        std::cerr << "Failed to acquire bus access or talk to the BME280\n";
        exit(1);
    }

}

bool BME280::begin(){
    // Configure the BME280 sensor
    std::cout << "BME280 config" << std::endl;

    try {
        writeRegister(BME280_REG_CTRL_HUM, 0x01);  // Humidity oversampling x1
        writeRegister(BME280_REG_CTRL_MEAS, 0x27); // Normal mode, oversampling x1 for temperature
        writeRegister(BME280_REG_CONFIG, 0xA0); // Set config (filter off, standby)
    }catch(const std::exception& e){
        std::cerr << "Caught an exception: " << e.what() << std::endl;
        exit(1);
    }

    std::cout << "End of BME280 config" << std::endl;

    return true;
}

float BME280::readTemperature(){

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
        
        std::ostringstream oss;
        oss << "Failed to write to register 0x"
            << std::hex << static_cast<int>(reg)
            << " with value 0x" << std::hex << static_cast<int>(value) << ".";

        throw std::runtime_error(oss.str());
    }
}

float BME280::compensateTemperature(int32_t rawTemp) {
    int32_t var1, var2;
    int32_t t_fine;

    // Read the calibration data (unsigned and signed as per datasheet)
    uint16_t dig_T1 = read16(0x88);             // Unsigned 16-bit
    int16_t dig_T2, dig_T3;
    dig_T2 = (int16_t)read16(0x8A);     // Signed 16-bit
    dig_T3 = (int16_t)read16(0x8C);     // Signed 16-bit

    // Debug print calibration values
    // std::cout << "Calibration data: dig_T1 = " << dig_T1 
    //           << ", dig_T2 = " << dig_T2 << ", dig_T3 = " << dig_T3 << std::endl;

    // Apply compensation formula - ADD EXPLICIT CASTS TO INT32_T TO HANDLE SIGNED/UNSIGNED CORRECTLY
    var1 = ((((int32_t)rawTemp >> 3) - ((int32_t)dig_T1 << 1)) * (int32_t)dig_T2) >> 11;
    var2 = ((((((int32_t)rawTemp >> 4) - (int32_t)dig_T1) * 
            ((int32_t)rawTemp >> 4) - (int32_t)dig_T1) >> 12) * (int32_t)dig_T3) >> 14;

    t_fine = var1 + var2;

    // Debug print intermediate values
    // std::cout << "var1: " << var1 << " var2: " << var2 << " t_fine: " << t_fine << std::endl;

    // Calculate temperature (same as Python)
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

    return (buffer[1] << 8 | buffer[0]);

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
