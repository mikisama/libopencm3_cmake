# LibOpenCM3 CMake

This project shows how to integrate LibOpenCM3 with CMake.

### Prerequisites

* [CMake](https://github.com/Kitware/CMake/releases)
* [GCC](https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases)
* [Ninja](https://github.com/ninja-build/ninja/releases)
* [Python](https://www.python.org/downloads)

### Quick Start

1. Create a app projetc
    ```bash
    git init libopencm3_app
    cd libopencm3_app
    ```
2. Add this repo as a submodule to `libopencm3_app`
    ```bash
    git submodule add https://github.com/mikisama/libopencm3_cmake.git libs/libopencm3_cmake
    git submodule update --init --recursive
    ```
3. Add `src/main.c`
    ```c
    #include <libopencm3/stm32/rcc.h>

    int main(void)
    {
        rcc_periph_clock_enable(RCC_GPIOA);

        for (;;)
        {
            asm("nop");
        }
    }
    ```
4. add `cmake/gcc-arm-none-eabi.cmake`
    ```cmake
    set(CMAKE_SYSTEM_NAME Generic)
    set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

    # This file assumes that path to the GCC toolchain is added
    # to the environment(PATH) variable, so that CMake can find

    find_program(CMAKE_C_COMPILER arm-none-eabi-gcc)

    macro(__flag_init lang)
        set(CMAKE_EXECUTABLE_SUFFIX_${lang} ".elf")
        set(CMAKE_${lang}_FLAGS_DEBUG "-Og -g -ggdb3")
        set(CMAKE_${lang}_FLAGS_MINSIZEREL "-Os -DNDEBUG")
        set(CMAKE_${lang}_FLAGS_RELEASE "-O3 -DNDEBUG")
        set(CMAKE_${lang}_FLAGS_RELWITHDEBINFO "-O2 -g -ggdb3 -DNDEBUG")
    endmacro()

    __flag_init(C)
    __flag_init(ASM)
    ```
5. Setup `CMakeLists.txt` like:
    ```cmake
    cmake_minimum_required(VERSION 3.16.0)

    project(opencm3_app
        LANGUAGES C ASM
    )

    add_compile_options(
        -mthumb
        -mcpu=cortex-m3
        -fdata-sections
        -ffunction-sections
        -Wall
        -Wextra
        --specs=nano.specs
        --specs=nosys.specs
    )

    add_link_options(
        -mthumb
        -mcpu=cortex-m3
        -nostartfiles
        -Wl,--gc-sections
        --specs=nano.specs
        --specs=nosys.specs
    )

    set(MCU_VARIANT stm32f103cb)
    set(OPENCM3_LIB opencm3_stm32f1)
    set(LIBOPENCM3_CMAKE_DIR libs/libopencm3_cmake)

    add_subdirectory(${LIBOPENCM3_CMAKE_DIR} ${OPENCM3_LIB})

    set(APP_SRCS
        ${CMAKE_CURRENT_LIST_DIR}/src/main.c
    )

    set(APP_INCS
        ${CMAKE_CURRENT_LIST_DIR}/src
    )

    add_executable(opencm3_app ${APP_SRCS})
    target_include_directories(opencm3_app PRIVATE ${APP_INCS})
    target_link_libraries(opencm3_app PRIVATE ${OPENCM3_LIB})
    target_link_options(opencm3_app
        PRIVATE
        -T ${CMAKE_BINARY_DIR}/generated.${MCU_VARIANT}.ld
        -Wl,-Map=opencm3_app.map
        -Wl,--print-memory
    )
    add_custom_command(
        TARGET opencm3_app
        POST_BUILD
        COMMAND ${CMAKE_OBJCOPY} -O srec opencm3_app.elf opencm3_app.srec
        BYPRODUCTS opencm3_app.srec
    )
    ```
6. Setup CMake build directory
    ```bash
    cmake -GNinja -DCMAKE_TOOLCHAIN_FILE='cmake/gcc-arm-none-eabi.cmake' -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Debug -Bbuild .
    ```
7. Build
    ```bash
    cmake --build build
    ```
