import time
from i2c_driver.bme280 import BME280I2CDriver
from db_handler import init_db, save_temperature_to_db

def log_temperature(bme280):
    """TODO"""

    temperature = bme280.read_sensor_data()
    print(f"Temperature: {temperature:.2f} C")
    save_temperature_to_db(temperature)


def main():

    # Initialize sensor
    bme280 = BME280I2CDriver()
    bme280.setup_bme280()
    time.sleep(1)
    bme280.read_calibration_data()

    # Initialize the database
    init_db()

    # Capture and log temperature data every 5 seconds
    while True:
        log_temperature(bme280)
        time.sleep(5)

if __name__ == "__main__":
    main()