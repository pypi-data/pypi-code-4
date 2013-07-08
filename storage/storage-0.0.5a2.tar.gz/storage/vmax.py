import sys
import os
import shlex
import subprocess
from lxml import etree

class VMAXArrayException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class VMAXArray:
    """
    Provide commonly used commands as methods.
    """
    def __init__(self, SYMCLI_CONNECT, SID, SYMCLI_CONNECT_TYPE='REMOTE', SYMCLI_PATH='/opt/emc/SYMCLI/bin/'):
        """
        Set environmental variables which will be used to run SYMCLI commands.
        """
        os.environ['PATH'] += os.pathsep + SYMCLI_PATH
        self.SYMCLI_CONNECT_TYPE = SYMCLI_CONNECT_TYPE
        self.SYMCLI_CONNECT = SYMCLI_CONNECT
        self.SID = str(SID)

    def __repr__(self):
        """
        Return a representation string
        """
        return "<%s - %s (SID:%s)>" % (self.__class__.__name__, self.SYMCLI_CONNECT, self.SID)

    def command(self, cmd, SYMCLI_OUTPUT_MODE='Standard'):
        """Run the command and return"""
        os.environ['SYMCLI_CONNECT_TYPE'] = self.SYMCLI_CONNECT_TYPE
        os.environ['SYMCLI_CONNECT'] = self.SYMCLI_CONNECT
        os.environ['SYMCLI_SID'] = str(self.SID)
        os.environ['SYMCLI_OUTPUT_MODE'] = SYMCLI_OUTPUT_MODE
        try:
            output = subprocess.check_output(shlex.split(cmd))
            return output
        except subprocess.CalledProcessError, e:
            raise VMAXArrayException("Command %s failed to execute successfully. Exception: %s" % (cmd, e))

    def command_xml(self, cmd):
        """
        Returns etree parsed XML which can be used to run find or xpath methods to retrieve details.
        """
        xml_output = self.command(cmd, 'XML_ELEMENT')
        return etree.XML(xml_output)


    def symcfgDiscover(self):
        self.command('symcfg disc')

    def getSymmInfo(self):
        doc = self.command_xml('symcfg list')
        return {
            'symid':doc.xpath('//symid/text()')[0],
            'attachment':doc.xpath('//attachment/text()')[0],
            'model':doc.xpath('//model/text()')[0],
            'microcode_version':doc.xpath('//microcode_version/text()')[0],
            'cache_megabytes': doc.xpath('//cache_megabytes/text()')[0],
            'devices': doc.xpath('//devices/text()')[0],
            'physical_devices': doc.xpath('//physical_devices/text()')[0],
        }

    def getDiskGroupSummary(self):
        doc = self.command_xml('symdisk list -dskgrp_summary -v')

        disk_groups = []
        for dg in doc.xpath('//Disk_Group'):
            dg_dct = {}
            for dg_info in dg.xpath('Disk_Group_Info/*'):
                dg_dct[dg_info.tag] = dg_info.text
            for dg_total in dg.xpath('Disk_Group_Totals/*'):
                dg_dct[dg_total.tag] = dg_total.text
            disk_groups.append(dg_dct)

        disk_group_summary = {}
        for summary in doc.xpath('//Disk_Group_Summary_Totals/*'):
            disk_group_summary[summary.tag] = summary.text

        dct = {
            'symid': doc.xpath('//Symm_Info/symid/text()')[0],
            'disk_groups': disk_groups,
            'disk_group_summary': disk_group_summary,
        }
        return dct

    def getThinPoolDetail(self):
        doc = self.command_xml('symcfg list -pool -thin -detail')
        thin_pools = []
        for tp in doc.xpath('//DevicePool'):
            dct = {}
            for tp_details in tp.xpath('*'):
                dct[tp_details.tag] = tp_details.text
            thin_pools.append(dct)
        return thin_pools

    def getPortGroup(self, verbose=True):
        if verbose:
            doc = self.command_xml('symaccess list -type port -v')
        else:
            doc = self.command_xml('symaccess list -type port')
