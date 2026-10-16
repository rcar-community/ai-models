# Copyright (C) 2026 Renesas Electronics Corporation
# Licensed under the Apache License, Version 2.0 (see LICENSES/Apache-2.0.txt).

cmake_minimum_required(VERSION 3.15)

if (NOT TARGET rcar_app_flags)
    message(FATAL_ERROR
        "missing the rcar_app_flags target! this CMakeLists must "
        "be added as a child of the app generator CMakeLists."
    )
endif()

if(NOT DEFINED ENV{TARGET_SOC})
	message(FATAL_ERROR "missing TARGET_SOC")
endif()
if(NOT DEFINED ENV{MODEL_ROOT})
	message(FATAL_ERROR "missing MODEL_ROOT")
endif()
if(NOT DEFINED ENV{TARGET_MODEL})
	message(FATAL_ERROR "missing TARGET_MODEL")
endif()

set(MODEL_ROOT   "$ENV{MODEL_ROOT}")
set(TARGET_MODEL "$ENV{TARGET_MODEL}")
set(TARGET_SOC   "$ENV{TARGET_SOC}")

if(NOT IS_ABSOLUTE "${MODEL_ROOT}")
	message(FATAL_ERROR "MODEL_ROOT is not absolute")
endif()

set(MODEL_HOME "${MODEL_ROOT}/${TARGET_MODEL}/${OUTPUT_PATH}/models")

if("$ENV{TARGET_OS}" STREQUAL "qnx")
	set(CMAKE_CXX_COMPILER "aarch64-unknown-nto-qnx7.1.0-gcc")
endif()

add_library(rcar_app_prepostproc STATIC prepostproc.cc)
target_link_libraries(rcar_app_prepostproc PRIVATE rcar_app_flags)

set(MODEL_FILES "")

function(model name)
	add_custom_command(
		OUTPUT  ".${name}-extracted"
		COMMAND rm -rf "${name}"
		COMMAND mkdir  "${name}"
		COMMAND tar -xvf "${MODEL_HOME}/${name}.tar" -C "${name}"
		COMMAND touch ".${name}-extracted"
		DEPENDS "${MODEL_HOME}/${name}.tar"
		COMMENT "extracting models/model_${name}.tar"
	)
	add_custom_command(
		OUTPUT  "${MODEL_HOME}/${name}.so"
		COMMAND "${CMAKE_CXX_COMPILER}" -shared --sysroot=${SYSROOT_PATH} -o "${MODEL_HOME}/${name}.so" "${name}/*"
		DEPENDS ".${name}-extracted"
		COMMENT "linking ${MODEL_HOME}/${name}.so"
	)
	set(MODEL_FILES "${MODEL_FILES};${MODEL_HOME}/${name}.so" PARENT_SCOPE)
endfunction()

model(model_cnnip)
model(model_dsp0)
model(model_dsp1)
model(model_dsp2)
model(model_dsp3)

add_custom_target(rcar_app_models DEPENDS ${MODEL_FILES})
