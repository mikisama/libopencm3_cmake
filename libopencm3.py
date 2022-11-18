# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
libOpenCM3
The libOpenCM3 framework aims to create a free/libre/open-source
firmware library for various ARM Cortex-M0(+)/M3/M4 microcontrollers,
including ST STM32, Ti Tiva and Stellaris, NXP LPC 11xx, 13xx, 15xx,
17xx parts, Atmel SAM3, Energy Micro EFM32 and others.
http://www.libopencm3.org
"""

# source: adapted from
# https://github.com/platformio/builder-framework-libopencm3

import argparse
import re
import sys
from os.path import dirname, isfile, join, normpath


def parse_makefile_data(makefile):
    data = {"includes": [], "objs": [], "vpath": ["./"]}

    with open(makefile) as f:
        content = f.read()

        # fetch "includes"
        re_include = re.compile(r"^include\s+([^\r\n]+)", re.M)
        for match in re_include.finditer(content):
            data["includes"].append(match.group(1))

        # fetch "vpath"s
        re_vpath = re.compile(r"^VPATH\s*\+?=\s*([^\r\n]+)", re.M)
        for match in re_vpath.finditer(content):
            data["vpath"] += match.group(1).split(":")

        # fetch obj files
        objs_match = re.search(
            r"^OBJS\s*\+?=\s*([^\.]+\.o\s*(?:\s+\\s+)?)+", content, re.M
        )
        assert objs_match
        data["objs"] = re.sub(r"(OBJS|[\+=\\\s]+)", "\n", objs_match.group(0)).split()
    return data


def get_source_files(src_dir):
    mkdata = parse_makefile_data(join(src_dir, "Makefile"))

    for include in mkdata["includes"]:
        _mkdata = parse_makefile_data(normpath(join(src_dir, include)))
        for key, value in _mkdata.items():
            for v in value:
                if v not in mkdata[key]:
                    mkdata[key].append(v)

    sources = []
    for obj_file in mkdata["objs"]:
        src_file = obj_file[:-1] + "c"
        for search_path in mkdata["vpath"]:
            src_path = normpath(join(src_dir, search_path, src_file))
            if isfile(src_path):
                sources.append(src_path)
                break
    return sources


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-V",
        "--variant",
        help="set the mcu variant (eg. stm32f103cb)",
        required=True,
    )

    args = parser.parse_args()

    variant = args.variant

    if variant.startswith("stm32"):
        vendor = variant[0:5]
        series = variant[5:7]
    else:
        sys.stderr.write("Currently, only support stm32 series")
        sys.exit(1)

    src_dir = join(dirname(__file__), "libopencm3/lib", vendor, series)
    sources = get_source_files(src_dir)
    srcs = " ".join(sources).replace("\\", "/")
    sys.stdout.write(srcs)


if __name__ == "__main__":
    main()
