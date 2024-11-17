import os
import struct
import time
from python_driver.bme280 import BME280I2CDriver
from db_handler import init_db, save_temperature_to_db

PIPE_NAME = "/tmp/sensor_pipe"

def log_temperature(bme280):
    """
    Util function to make a call to the python sensor driver and save the returned temperature to the database.
    """

    temperature = bme280.read_sensor_data()
    print(f"Temperature: {temperature:.2f} C")
    save_temperature_to_db(temperature)


def main_python():
    """
    Main function if we want to use the python sensor driver
    """

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

def main_cpp():
    """
    Function to use the c++ sensor driver to receive the temperature data wia a named pipe and save it to a database.
    """

    # Initialize the database
    init_db()

    # Open pipe for Inter Process communication
    with open(PIPE_NAME, 'rb') as pipe: # Blocking if no process has opened the pipe in write mode (O_WRONLY)
        print("Opened pipe for reading")

        try:
            while True:
                # Read the temperature data (float is 4 bytes)
                data = pipe.read(4)
                if not data:
                    break

                # Unpack binary into float
                temperature = struct.unpack('f', data)[0]
                print(f"Received temperature: {temperature:.2f} °C")

                save_temperature_to_db(temperature)
        
        except KeyboardInterrupt:
            print('Process interrupted.')

if __name__ == "__main__":
    # main_python()
    main_cpp()