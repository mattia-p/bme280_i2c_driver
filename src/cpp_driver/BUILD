cc_library(
    name = "bme280_cpp_driver",
    srcs = ["bme280_cpp_driver.cpp"],
    hdrs = ["bme280_cpp_driver.h"],
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "bme280_cpp_driver_executable",
    srcs = ["main.cpp"],
    deps = [":bme280_cpp_driver"],
)