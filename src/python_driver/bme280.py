import smbus2
import time

class BME280I2CDriver:

	# Default I2C address
	BME280_I2C_ADDRESS = 0x77

	# Control and configuration registers
	BME280_REG_ID = 0xD0
	BME280_REG_RESET = 0xE0
	BME280_REG_CTRL_HUM = 0xF2
	BME280_REG_CTRL_MEAS = 0xF4
	BME280_REG_CONFIG = 0xF5

	# Data registers
	BME280_REG_PRESS_MSB = 0xF7
	BME280_REG_PRESS_LSB = 0xF8
	BME280_REG_PRESS_XLSB = 0xF9
	BME280_REG_TEMP_MSB = 0xFA
	BME280_REG_TEMP_LSB = 0xFB
	BME280_REG_TEMP_XLSB = 0xFC
	BME280_REG_HUM_MSB = 0xFD
	BME280_REG_HUM_LSB = 0xFE

	# Calibration registers
	REG_CALIB_00 = 0x88
	REG_CALIB_25 = 0xA1
	REG_CALIB_HUM = 0xE1

	# Default configuration values
	HUM_OVERSAMPLING_X1 = 0x01
	TEMP_PRESS_OVERSAMPLING_X1 = 0x27
	CONFIG_DEFAULT = 0xA0

	def __init__(self):
		self.bus = smbus2.SMBus(1) # I2C bus 1 on pi
		self.address = self.BME280_I2C_ADDRESS
		self.calibration_data = []
		self.t_fine = 0
		
	def read_byte(self, register):
		return self.bus.read_byte_data(self.address, register)

	def read_calibration_data(self):
		""" Reading calibration data needed for temperature, pressure and humidity compensation"""

		calib = []
	
		# Read calibration registers for temperature and pressure
		for i in range(self.REG_CALIB_00, self.REG_CALIB_00 + 24):
			calib.append(self.read_byte(i))
			
		# Read the calibration registers for humidity
		calib.append(self.read_byte(self.REG_CALIB_25))
		
		for i in range(self.REG_CALIB_HUM, self.REG_CALIB_HUM + 7):
			calib.append(self.read_byte(i))
			
		self.calibration_data = calib

	def setup_bme280(self):
		""" Initial BME280 setup"""
		# Read the sensor ID. Just to make sure the sensor is connected
		chip_id = self.read_byte(self.BME280_REG_ID)
		if chip_id != 0x60:
			raise RuntimeError("BME280 not found or wrong device ID.")
					
		# Configure the sensor

		# Humidity oversampling x1 (1 sample)
		self.bus.write_byte_data(self.address, self.BME280_REG_CTRL_HUM, 0x01) 
		# Pressure and temp oversampling x1, mode normal. The value of 0x27 sets the temp and pressure oversampling to 1 and the mode to normal (the sensor continuously takes measurements).
		self.bus.write_byte_data(self.address, self.BME280_REG_CTRL_MEAS, 0x27) 
		# Standby 1000ms, filter off. Standy time (time the sensor waits between measurements). Filter to smooth out noise in measurements
		self.bus.write_byte_data(self.address, self.BME280_REG_CONFIG, 0xA0) 


	def read_raw_data(self):
		""" Read raw temperature, pressure and humidity data"""
	
		# Read 8 consecutive bytes, starting from the pressure's most significant byte (MSB) register
		data = self.bus.read_i2c_block_data(self.address, self.BME280_REG_PRESS_MSB, 8)
		
		raw_pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
		raw_temperature = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4) 
		raw_humidity = (data[6] << 8) | data[7]
		
		return raw_temperature, raw_pressure, raw_humidity

	def compensate_temperature(self, raw_temp):
		"""Applies temperature compensation using calibration data"""
	
		dig_T1 = (self.calibration_data[1] << 8) | self.calibration_data[0]
		dig_T2 = (self.calibration_data[3] << 8) | self.calibration_data[2]
		dig_T3 = (self.calibration_data[5] << 8) | self.calibration_data[4]
		
		var1 = ((((raw_temp >> 3) - (dig_T1 << 1))) * dig_T2) >> 11
		var2 = (((((raw_temp >> 4) - dig_T1) ** 2) >> 12) * dig_T3) >> 14

		
		self.t_fine = var1 + var2
		
		# Actual temperature in celcius
		temperature = (self.t_fine * 5 + 128) // 256
		
		return temperature / 100.0


	def compensate_pressure(self, raw_pressure):
		pass

	def compensate_humidity(self, raw_humidity):
		pass

	def read_sensor_data(self):
		"""Reads raw sensor data and applies the compensation formulas"""

		try:
			raw_temp, raw_pressure, raw_humidity = self.read_raw_data()
		except IOError:
			raise RuntimeError("Error communicating with the sensor")
			
		temperature = self.compensate_temperature(raw_temp) # °C
		# pressure = self.compensate_pressure(raw_pressure) # hPa
		# humidity = self.compensate_humidity(raw_humidity) # %

		return temperature


def main():
	
	bme280 = BME280I2CDriver()
	bme280.setup_bme280()

	time.sleep(1)

	bme280.read_calibration_data()
	
	temperature = bme280.read_sensor_data()

	print(f"Temperature: {temperature:.2f} C")

if __name__ == "__main__":
	main()
