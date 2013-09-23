# Copyright (c) 2013, Calxeda Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of Calxeda Inc. nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import process_types
import subprocess
import os
import struct

FruMagicNum = 0x786c6163
FruFlatPartType = 1
FruKVPartType = 2

FruX04Size = 2048
FruX04Offset = FruX04Size

FruPartitionTblStart = 32
FruPartitionTblEntrySize = 16
FruPartitionTblMaxEntries = 8

__data_offsets = {}

def verify_partition_config(config, dev_size):
    # start of the partitions is the end of the partition table
    data_end = FruPartitionTblStart
    data_end += FruPartitionTblEntrySize * (FruPartitionTblMaxEntries + 1)
    for part_cfg in config:
        if part_cfg["type"] > 255 or part_cfg["type"] <= 0:
            sys.stderr.write("Invalid type: " + repr(part_cfg["type"]) + "\n")
            sys.exit(1)
        if part_cfg["id"] > 255 or part_cfg["id"] <= 0:
            sys.stderr.write("Invalid id: " + repr(part_cfg["type"]) + "\n")
            sys.exit(1)

        # If the image_file is not already set, open the file
        if part_cfg.get("image_file",None) == None:
            filename = part_cfg.get("image",None)
            if filename != None:
                file = open(filename)
            else:
                file = None
            part_cfg["image_file"] = file

        # figure out start and end if not provided
        if part_cfg.get("start", None) == None:
            part_cfg["start"] = data_end
            part_cfg["end"] = data_end + part_cfg["size"]
            size = part_cfg["size"]
        else:
            size = part_cfg["end"] - part_cfg["start"]
        data_end += size

    if data_end > dev_size:
            sys.stderr.write("Not enough space for all the partitions\n")
            sys.exit(1)


def create_fru_image(fru_image, configs, version, capacity, is_x04):
    if(is_x04):
        count = 4
    else:
        count = 1

    zero_file(fru_image, capacity)

    marshal_dict = process_types.get_marshal_dict()
    key_ids = process_types.get_key_nums()

    config_locals = process_types.get_symbols()
    config_locals['kv_config_data'] = {}

    i = 0
    for node_cfg in configs:
        part_offset = i * FruX04Offset
        write_header(fru_image, capacity, version, is_x04, 0, part_offset)
        if version > 1:
            write_partition_tbl(fru_image, node_cfg, part_offset)

        # write partitions
        for part_cfg in node_cfg:
            if part_cfg["type"] == FruFlatPartType:
                write_mfg_image(fru_image, part_cfg.get("image_file",None),
                                part_cfg["start"], part_cfg["end"],
                                part_offset)
                continue
            if part_cfg["type"] == FruKVPartType:
                # read kv config file data into var kv_config_data
                config_str = part_cfg["image_file"].read()
                exec("kv_config_data = " + config_str, globals(), config_locals)
                config_data = config_locals['kv_config_data']
                if config_data.get('cfg_version',None) == None:
                    version_str = get_version_str(part_cfg["image"])
                    config_data['cfg_version'] = version_str
                num_commits = get_num_commits(part_cfg["image"])
                config_data['file_version'] = num_commits
                write_kv_data(fru_image, config_data,
                              key_ids, marshal_dict, part_cfg["start"],
                              part_cfg["end"], part_offset)
                continue
        i += 1

def get_version_str(filename):
    try:
        git_desc_str = subprocess.check_output(['git', 'describe', '--dirty', '--always'])
    except subprocess.CalledProcessError:
        git_desc_str = 'Unknown'
    return git_desc_str.rstrip()


def get_num_commits(filename):
    try:
        command = "git log --pretty=oneline %s 2> /dev/null | wc -l" % filename
        num_commits_str = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        num_commits_str = 'Unknown'
    return num_commits_str.rstrip()


def zero_file(fru_image, size):
    fru_image.seek(0)
    for i in range(size /4):
        fru_image.write('\0\0\0\0')


def write_header(fru_image, size, version=1, x04=False,
                reserved=0, partition_offset=0):
    if(x04):
        flags = 0x01
        size = FruX04Size
    else:
        flags = 0
    header = struct.pack('<IIIII', FruMagicNum, version, size, flags, reserved)
    fru_image.seek(partition_offset)
    fru_image.write(header)

def write_partition_tbl(fru_image, config, partition_offset=0):
    fru_image.seek(partition_offset + FruPartitionTblStart)
    for part_cfg in config:
        write_part_tbl_entry(fru_image, part_cfg["type"], part_cfg["id"],
                             part_cfg["start"], part_cfg["end"],
                             partition_offset)

def write_part_tbl_entry(fru_image, type, id, start, end, partition_offset,
                         reserved1=0, reserved2=0):
    entry = struct.pack('<BBHIII', type, id, reserved1, start, end, reserved2)
    fru_image.write(entry)


def write_tuple(fru_image, key, data, device_offset, name):
    tuple_header = struct.pack('<HH', key, len(data))
    save_data_offset(name, device_offset + 4)
    fru_image.write(tuple_header)
    fru_image.write(data)
    return len(tuple_header) + len(data)


def write_mfg_image(fru_image, mfg_image, part_start, part_end,
                    partition_offset=0):
    if (mfg_image == None):
        return
    mfg_image.seek(0)
    data = mfg_image.read(part_end - part_start)
    fru_image.seek(partition_offset + part_start)
    fru_image.write(data)


def write_kv_data(fru_image, fru_data, keys, marshal_dict,
                  part_start, part_end, partition_offset=0):
    space_remaining = part_end - part_start;
    device_offset = partition_offset + part_start
    fru_image.seek(device_offset)
    data_sorted_by_key_num = sorted(fru_data.iteritems(),
                                    key=lambda pair: keys[pair[0]])
    for name, value in data_sorted_by_key_num:
        bin_data = marshal_dict[name](value)
        t_sz = write_tuple(fru_image, keys[name], bin_data, device_offset, name)
        device_offset += t_sz
        space_remaining -= t_sz
        if (space_remaining < 0):
            sys.stderr.write("A KV partition has overflowed")
            sys.stderr.write(" (too much data in config file)\n")
            sys.stderr.write("Size: " + repr(part_end - part_start) + "\n")
            sys.exit(1)


def save_data_offset(name, data_loc):
    __data_offsets[name] = data_loc


def dump_offsets_to_file(csv_file):
    offsets_sorted = sorted(__data_offsets.iteritems(),
                            key=lambda pair: pair[1])
    for name, offset in offsets_sorted:
        csv_file.write("%s,%s\n" % (name, hex(offset)))

