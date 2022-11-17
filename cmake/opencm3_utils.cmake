# opencm3_add_stm32_library(stm32f103c8)

function(opencm3_add_stm32_library variant)
    # variant       stm32f103c8
    # vendor        stm32
    # series        f1
    # vendor_upper  STM32
    # series_upper  F1
    string(SUBSTRING ${variant} 0 5 vendor)
    string(SUBSTRING ${variant} 5 2 series)
    string(TOUPPER ${vendor} vendor_upper)
    string(TOUPPER ${series} series_upper)

    execute_process(COMMAND
        python
        ./libopencm3.py
        -V
        ${variant}
        OUTPUT_VARIABLE
        OPENCM3_SRCS
        WORKING_DIRECTORY
        ${OPENCM3_ROOT_DIR}/../
    )

    separate_arguments(OPENCM3_SRCS)

    set(OPENCM3_INCS
        ${OPENCM3_ROOT_DIR}/include
    )

    add_library(opencm3_${vendor}${series} STATIC ${OPENCM3_SRCS})
    target_include_directories(opencm3_${vendor}${series} PUBLIC ${OPENCM3_INCS})
    target_compile_definitions(opencm3_${vendor}${series} PUBLIC ${vendor_upper}${series_upper})

    execute_process(COMMAND
        python
        ./scripts/genlink.py
        ./ld/devices.data
        ${variant}
        DEFS
        OUTPUT_VARIABLE
        GENLINK_DEFS
        WORKING_DIRECTORY
        ${OPENCM3_ROOT_DIR}
    )

    separate_arguments(GENLINK_DEFS)

    add_custom_target(irq2nvic_${vendor}${series}
        COMMAND
        python
        ./scripts/irq2nvic_h
        ./include/libopencm3/${vendor}/${series}/irq.json
        BYPRODUCTS
        ${OPENCM3_ROOT_DIR}/include/libopencm3/${vendor}/${series}/nvic.h
        ${OPENCM3_ROOT_DIR}/lib/${vendor}/${series}/vector_nvic.c
        WORKING_DIRECTORY
        ${OPENCM3_ROOT_DIR}
    )

    add_custom_target(genlink_${vendor}${series}
        COMMAND
        ${CMAKE_C_COMPILER}
        -P
        -E
        ${GENLINK_DEFS}
        ./ld/linker.ld.S
        -o
        ${CMAKE_BINARY_DIR}/generated.${variant}.ld
        BYPRODUCTS
        ${CMAKE_BINARY_DIR}/generated.${variant}.ld
        WORKING_DIRECTORY
        ${OPENCM3_ROOT_DIR}
    )

    add_dependencies(opencm3_${vendor}${series} irq2nvic_${vendor}${series})
    add_dependencies(opencm3_${vendor}${series} genlink_${vendor}${series})
endfunction()
