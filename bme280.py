import smbus2
import time

BME280_I2C_ADDRESS = 0x77

# BME280 registers
BME280_REG_ID = 0xD0
BME280_REG_RESET = 0xE0
BME280_REG_CTRL_HUM = 0xF2
BME280_REG_CTRL_MEAS = 0xF4
BME280_REG_CONFIG = 0xF5
BME280_REG_PRESS_MSB = 0xF7

# Create an I2C bus object
bus = smbus2.SMBus(1) # I2C bus 1 on pi

def read_byte(register):
	return bus.read_byte_data(BME280_I2C_ADDRESS, register)
	
def read_calibration_data():
	# Reading calibration data needed for temperature, pressure and humidity compensation
	
	calib = []
	
	for i in range(0x88, 0x88 + 24):
		calib.append(bus.read_byte_data(BME280_I2C_ADDRESS, i))
		
	calib.append(bus.read_byte_data(BME280_I2C_ADDRESS, 0xA1))
	
	for i in range(0xE1, 0xE1 + 7):
		calib.append(bus.read_byte_data(BME280_I2C_ADDRESS, i))
		
	return calib

def setup_bme280():
	print('Setup BME280')
	
	# Read the sensor ID. Just to make sure the sensor is connected
	chip_id = read_byte(BME280_REG_ID)
	if chip_id != 0x60:
		raise RuntimeError("BME280 not found or wrong device ID.")
		
	print('chip_id: ', chip_id)
	
	# Configure the sensor
	bus.write_byte_data(BME280_I2C_ADDRESS, BME280_REG_CTRL_HUM, 0x01) # Humidity oversampling x1 (1 sample)
	bus.write_byte_data(BME280_I2C_ADDRESS, BME280_REG_CTRL_MEAS, 0x27) # Pressure and temp oversampling x1, mode normal. The value of 0x27 sets the temp and pressure oversampling to 1 and the mode to normal (the sensor continuously takes measurements).
	bus.write_byte_data(BME280_I2C_ADDRESS, BME280_REG_CONFIG, 0xA0) # Standby 1000ms, filter off. Standy time (time the sensor waits between measurements). Filter to smooth out noise in measurements

def compensate_temperature(raw_temperature, calib):
	"""Applies temperature compensation using calibration data."""
	
	dig_T1 = (calib[1] << 8) | calib[0]
	dig_T2 = (calib[3] << 8) | calib[2]
	dig_T3 = (calib[5] << 8) | calib[4]
	
	var1 = ((((raw_temperature // 8) - (dig_T1 * 2))) * dig_T2) // 2048
	var2 = (((((raw_temperature // 16) - dig_T1) ** 2) // 4096) * dig_T3) // 16384
	
	t_fine = var1 + var2
	
	# Actual temperature in celcius
	temperature = (t_fine * 5 + 128) // 256
	
	return temperature / 100.0, t_fine

	
		
def read_raw_data():
	
	# Read raw temperature, pressure and humidity data
	
	# Read 8 consecutive bytes, starting from the pressure's most significant byte (MSB) register
	data = bus.read_i2c_block_data(BME280_I2C_ADDRESS, BME280_REG_PRESS_MSB, 8)
	
	raw_pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
	raw_temperature = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4) 
	raw_humidity = (data[6] << 8) | data[7]
	
	return raw_temperature, raw_pressure, raw_humidity

def main():
	setup_bme280()
	
	time.sleep(1)
	
	# Reading calibration data for compensation formulas (required)
	calibration_data = read_calibration_data()
	
	# Read raw sensor data
	raw_temperature, raw_pressure, raw_humidity = read_raw_data()
	
	print(f"Raw temperature: {raw_temperature}")
	print(f"Raw pressure: {raw_pressure}")
	print(f"Raw humidity: {raw_humidity}")
	
	# Apply compensation formulas
	temperature, t_fine = compensate_temperature(raw_temperature, calibration_data)
	
	print(f"Temperature: {temperature:.2f} C")


if __name__ == "__main__":
	main()
