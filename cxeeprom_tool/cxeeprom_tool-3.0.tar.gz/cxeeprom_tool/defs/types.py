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

basic_data_types = {
                'int32_t': 'i',
                'uint32_t': 'I',
                'int16_t': 'h',
                'uint16_t': 'H',
                'int8_t': 'b',
                'uint8_t': 'B',
                'char': 'c'
                }


data_types = {
            'version_string' : {
                        'type' : 'string',
                        'length' : 40
                        },
            'cfg_revision_string' : {
                        'type' : 'string',
                        'length' : 4
                        },
            'board_id' : {
                    'type' : 'enum',
                    'size' : 'uint32_t',
                    'constants' : {
                                   "INVALID" : -1,
                                   "TILE" : 0,
                                   "ENERGYCARD" : 1,
                                   "COOPER4" : 3,
                                   "SLINGSHOT" : 7,
                                   "CUMULUS" : 8,
                                   "CATAPULT" : 9,
                                   "DUAL_NODE" : 10,
                                   "DUAL_NODE_UPLINK" : 11,
				   "TN_CMC" : 12,
                                  },
                    },
            'sysboard_id' : {
                    'type' : 'enum',
                    'size' : 'uint32_t',
                    'constants' : {
                                   "SYSBRD_INVALID" : -1,
                                   "SYSBRD_SBXX" : 1,
                                   "SYSBRD_COOPER4" : 3,
                                   "SYSBRD_SLINGSHOT" : 7,
                                   "SYSBRD_CUMULUS" : 8,
                                   "SYSBRD_CATAPULT" : 9,
                                   "SYSBRD_TN_WEB" : 10,
                                   "SYSBRD_TN_STORAGE" : 11,
                                  },
                    },
            'sysboard_str' : {
                    'type' : 'string',
                    'length' : 80,
                    },
            'serial_num' : {
                    'type' : 'string',
                    'length' : 24,
                    },
            'phy_config' : {
                    'type' : 'struct',
                    'members' : [
                                ('type','connection_type','connectionType', None),
                                ('fabric_mode','fabric_config_type','fabricMode', 'UNDEFINED'),
                                ('slot_lane', 'uint8_t', 'laneNum', 0xff),
                                ('destination', 'uint8_t', 'destinationNode', 0xff)
                                ]
                    },
            'node_phys' : {
                        'type' : 'array',
                        'member_type' : 'phy_config',
                        'length' : 6
                        },
            'slot_desc' : {
                    'type' : 'struct',
                    'members' : [
                                ('type','connection_type','connectionType', None),
                                ('fabric_mode','fabric_config_type','fabricMode', 'UNDEFINED'),
                                ('dest_lane', 'uint8_t', 'laneNum', 0xff),
                                ('dest_slot', 'uint8_t', 'destinationSlot', 0xff)
                                ]
                    },
            'slot_desc_arr' : {
                        'type' : 'array',
                        'member_type' : 'slot_desc',
                        'length' : 12
                        },
            'connection_type' : {
                    'type' : 'enum',
                    'size' : 'uint8_t',
                    'constants' : {
                                   "LANE" : 0,
                                   "DISABLED" : 1,
                                   "UPLINK" : 2,
                                   "INTERCONNECT" : 3,
                                   "MAC_LINK" : 4,
                                   "SGMII_MANAGE" : 5,
                                   "FABRIC_LINK" : 6,
                                   "SATAX4" : 7,
                                   "SATAX1" : 8,
                                   "PCIeX4" : 9,
                                   "PCIeX8" : 10
                                   }
                    },
            'fabric_config_type' : {
                    'type' : 'enum',
                    'size' : 'uint8_t',
                    'constants' : {
                                   "NEGOTIATED" : 1,
                                   "DISCOVERED" : 2,
                                   "x1G" : 3,
                                   "x10G" : 4,
                                   "UNDEFINED" : 0xff
                                   }
                    },
            'mac_address' : {
                    'type' : 'array',
                    'member_type' : 'uint8_t',
                    'length' : 6
                    },
            'oui' : {
                    'type' : 'array',
                    'member_type' : 'uint8_t',
                    'length' : 3
                    },
            'vendor_id' : {
                    'type' : 'enum',
                    'size' : 'uint32_t',
                    'constants' : {
                                   "VENDOR_INVALID" : -1,
                                   "VENDOR_CALXEDA" : 1,
                                  }
                    }
            }
