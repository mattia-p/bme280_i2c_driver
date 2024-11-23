#include "bme280_cpp_driver.h"

#include <fcntl.h> // File control operations, open...
#include <iostream> // cin, cout, cerr
#include <sys/stat.h> // For mkfifo() and stat()
#include <unistd.h>    // For unlink()


int main()
{
    BME280 sensor("/dev/i2c-1", BME280_ADDRESS);

    if (!sensor.begin())
    {
        std::cerr << "Failed to initialize BME280\n";
        return 1;
    }

    // Check if the named pipe exists before creating it
    struct stat st;
    if(stat(PIPE_NAME, &st) != 0){
        // Create the named pipe (FIFO) if it doesn't exist
        if(mkfifo(PIPE_NAME, 0666) == -1){ // Create a named pipe at the path /tmp/sensor_pipe with read/write permissions
            perror("mkfifo failed");
            return 1;
        }
    }

    // Open the pipe for writing
    int pipe_fd = open(PIPE_NAME, O_WRONLY); // Will block until a reader is available
    if (pipe_fd == -1){
        perror("Failed to open pipe for writing");
        return 1;
    }

    std::cout << "Begin loop" << std::endl;

    while (true){
        // Read temperature from the sensor
        float temperature = sensor.readTemperature();

        // Write the temperature to the pipe
        if (write(pipe_fd, &temperature, sizeof(temperature)) == -1) {
            perror("Failed to write to pipe");
            break;
        }

        std::cout << "Send temperature: " << temperature << " °C\n";
        sleep(1); // Send data every second
    }

    close(pipe_fd); // Close the pipe when done

    return 0;
}
