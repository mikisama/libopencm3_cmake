cmake_minimum_required(VERSION 3.16.0)

project(libopencm3
    LANGUAGES C ASM
)

set(OPENCM3_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR}/libopencm3)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/opencm3_utils.cmake)

if(NOT DEFINED MCU_VARIANT)
    message(FATAL_ERROR "ERROR: MCU_VARIANT not defined")
endif()

opencm3_add_stm32_library(${MCU_VARIANT})
