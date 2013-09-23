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

var_defs = {
            "cfg_version" : {"type" : "version_string", "id" : 1},

            "board_id" : {"type" : "board_id", "id" : 2},
            "board_rev" : {"type" : "int32_t", "id" : 3},
            "sys_board_i2c_bus" : {"type" : "int32_t", "id" : 4},
            "lanes_per_slot" : {"type" : "int32_t", "id" : 5},
            "emmc" : {"type" : "uint8_t", "id" : 6},
            "sysboard_id" : {"type" : "sysboard_id", "id" : 7},
            "sysboard_rev" : {"type" : "int32_t", "id" : 8},
            "vendor_id" : {"type" : "int32_t", "id" : 9},
            "board_str" : {"type" : "sysboard_str", "id" : 10},
            "file_version" : {"type" : "cfg_revision_string", "id" : 11},
            "chassis_serial_num" : {"type" : "serial_num", "id" : 12},

            "node_phys" : {"type" : "node_phys", "id" : 50},
            "slot_lanes" : {"type" : "slot_desc_arr", "id" : 51},

            "calxeda_mac_addr" : {"type" : "mac_address", "id" : 52},

            "oem_mac0_addr" : {"type" : "mac_address", "id" : 55},
            "oem_mac1_addr" : {"type" : "mac_address", "id" : 56},
            "oem_mac2_addr" : {"type" : "mac_address", "id" : 57},
            "oem_oui" : {"type" : "oui", "id" : 58},

            "slot_0_lanes" : {"type" : "slot_desc_arr", "id" : 100},
            "slot_1_lanes" : {"type" : "slot_desc_arr", "id" : 101},
            "slot_2_lanes" : {"type" : "slot_desc_arr", "id" : 102},
            "slot_3_lanes" : {"type" : "slot_desc_arr", "id" : 103},
            "slot_4_lanes" : {"type" : "slot_desc_arr", "id" : 104},
            "slot_5_lanes" : {"type" : "slot_desc_arr", "id" : 105},
            "slot_6_lanes" : {"type" : "slot_desc_arr", "id" : 106},
            "slot_7_lanes" : {"type" : "slot_desc_arr", "id" : 107},
            "slot_8_lanes" : {"type" : "slot_desc_arr", "id" : 108},
            "slot_9_lanes" : {"type" : "slot_desc_arr", "id" : 109},
            "slot_10_lanes" : {"type" : "slot_desc_arr", "id" : 110},
            "slot_11_lanes" : {"type" : "slot_desc_arr", "id" : 111},
            "slot_12_lanes" : {"type" : "slot_desc_arr", "id" : 112},
            "slot_13_lanes" : {"type" : "slot_desc_arr", "id" : 113},
            "slot_14_lanes" : {"type" : "slot_desc_arr", "id" : 114},
            "slot_15_lanes" : {"type" : "slot_desc_arr", "id" : 115},
            "slot_16_lanes" : {"type" : "slot_desc_arr", "id" : 116},
            "slot_17_lanes" : {"type" : "slot_desc_arr", "id" : 117},

            "sata_adj_start" : {"type" : "int32_t", "id" : (1024)},
            "sata_atten_adj_P0_L0" : {"type" : "int32_t", "id" : (1024+0+5)},
            "sata_atten_adj_P0_L1" : {"type" : "int32_t", "id" : (1024+32+5)},
            "sata_atten_adj_P0_L2" : {"type" : "int32_t", "id" : (1024+64+5)},
            "sata_atten_adj_P0_L3" : {"type" : "int32_t", "id" : (1024+96+5)},
            "sata_atten_adj_P5_L0" : {"type" : "int32_t", "id" : (1024+(32*4)+5)}
    }
