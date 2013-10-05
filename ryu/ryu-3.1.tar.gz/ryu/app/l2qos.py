# Copyright (C) 2013 Veryx Technologies Pvt Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    This module performs L2 learning for an incoming flow, assigns it
    to a specific egress port queue based on the flow's VLAN Pbit value and 
    adds the flow entry in the switch flow table. The queue assignment will be 
    based on default Pbit-Queue mapping defined by default in the module or 
    overwritten using user defined value Pbit-Queue mapping value. Any flows 
    received without VLAN tag will be assigned to Queue 1.
    
    The default Pbit-Queue mapping is {0:8, 1:7, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1} where
    0 denotes VLAN Pbit and 8 denotes Queue ID.  
"""

import logging
import struct
import ast

from oslo.config import cfg
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ether
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import vlan

# User-defined input
# Below code re-assigns the Pbit-Queue mapping for Queue ID 4 and 5 with Pbit 5 and 6
CONF = cfg.CONF
CONF.register_cli_opts([
    cfg.StrOpt('pcp-queue', default={5:4,6:5},
                help='pcp to queue map')
])


class L2QoS(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2QoS, self).__init__(CONF.pcp_queue,*args, **kwargs)
        self.mac_to_port = {}   # MAC Address table initialization
        self.pcp_queue = CONF.pcp_queue
        self.port = self.pcp_queue.keys()

    """
    This function installs the flow in the OpenFlow switch Flow Table
    """
    def add_flow(self, datapath, in_port, dst, vlan_pcp, _eth_type,nw_src, actions):
        ofproto = datapath.ofproto
        wildcards = ofproto_v1_0.OFPFW_ALL
        wildcards &= ~ofproto_v1_0.OFPFW_IN_PORT
        wildcards &= ~ofproto_v1_0.OFPFW_DL_DST
        if _eth_type == ether.ETH_TYPE_8021Q :
           wildcards &= ~ofproto_v1_0.OFPFW_DL_VLAN_PCP
           wildcards &= ~ofproto_v1_0.OFPFW_NW_SRC_MASK
           match = datapath.ofproto_parser.OFPMatch(
            wildcards, in_port, 0, dst,
            0, vlan_pcp, 0, 0, 0, nw_src, 0, 0, 0)
        elif _eth_type == ether.ETH_TYPE_IP :
           wildcards &= ~ofproto_v1_0.OFPFW_DL_TYPE
           wildcards &= ~ofproto_v1_0.OFPFW_NW_SRC_MASK
           match = datapath.ofproto_parser.OFPMatch(
            wildcards, in_port, 0, dst,
            0, 0, _eth_type, 0, 0, nw_src, 0, 0, 0)
        else :
           wildcards &= ~ofproto_v1_0.OFPFW_DL_TYPE
           match = datapath.ofproto_parser.OFPMatch(
            wildcards, in_port, 0, dst,
            0, 0, _eth_type, 0, 0, 0, 0, 0, 0)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

   
    """
    This function handles packet-in messages from the switch and performs L2 learning and vlan 
    pcp to queue mapping
    """
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        _eth_type = eth.ethertype
        
        print dst,src,_eth_type
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        #Learn new MAC Address from packet-in message.
        self.mac_to_port[dpid][src] = msg.in_port
        nw_src = 0
        #Flood the frame if destination MAC is unknown
        if dst not in self.mac_to_port[dpid] and haddr_to_str(dst) != 'ff:ff:ff:ff:ff:ff': 
            out_port = ofproto.OFPP_FLOOD
            self.logger.info("Port for %s unknown -- flooding" % haddr_to_str(dst))
        #Flood the frame if destination MAC is Broadcast
        elif haddr_to_str(dst) == 'ff:ff:ff:ff:ff:ff': 
            out_port = ofproto.OFPP_FLOOD
            self.logger.info("Destination address %s is broadcast -- flooding" % haddr_to_str(dst))
        #Forward the frame based on MAC Address table learnings
        elif dst in self.mac_to_port[dpid]: 
            out_port = self.mac_to_port[dpid][dst]
            self.logger.info("packet in %s %s %s %s",
                             dpid, haddr_to_str(src), haddr_to_str(dst),
                             msg.in_port)
            #Assign the flow to Queue ID 1 if the flow is untagged
            if _eth_type == 2048: 
               q_id = 1
               vlan_pcp = 0
               _eth_type = 0x0800
               a=struct.unpack_from('!6s6sHBxHBB2xIII', buffer(msg.data), 0)
               nw_src = a[8]
            #Assign the flow to the defined Queue ID if the flow is VLAN tagged
            elif _eth_type == 33024:
               _eth_type = 0x8100  
               vlan1q = pkt.get_protocols(vlan.vlan)[0]
               vlan_pcp = vlan1q.pcp
               if self.pcp_queue.keys().count(vlan_pcp) == 0 : 
                  dict = {0:8, 1:7, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1} #Default Pbit to Queue mapping
                  q_id = dict[vlan_pcp]
               else :
                  q_id = self.pcp_queue[vlan_pcp] #Overwrite Pbit to Queue mapping with user defined inputs
               a=struct.unpack_from('!6s6sHBxHBB2xIII', buffer(msg.data), 0)
               nw_src = a[9]   
            else : 
               q_id = 1
               vlan_pcp = 0            
        
        if out_port != ofproto.OFPP_FLOOD:
           actions = [datapath.ofproto_parser.OFPActionEnqueue(port=out_port,queue_id=q_id)]
           self.add_flow(datapath, msg.in_port, dst,vlan_pcp, _eth_type, nw_src, actions)
        elif out_port == ofproto.OFPP_FLOOD:
           actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        out = datapath.ofproto_parser.OFPPacketOut(
              datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
              actions=actions)
        datapath.send_msg(out)
#         out = datapath.ofproto_parser.OFPQueueGetConfigRequest(datapath=datapath,port=1)
#         datapath.send_msg(out)




