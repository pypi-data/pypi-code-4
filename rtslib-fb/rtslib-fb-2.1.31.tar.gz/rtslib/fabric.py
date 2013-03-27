'''
Copyright (c) 2011 by RisingTide Systems LLC
Copyright (c) 2013 by Andy Grover

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, version 3 (AGPLv3).

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Description
-----------

Fabrics may differ in how fabric WWNs are represented, as well as
what capabilities they support


Available parameters
--------------------

* features
Lists the target fabric available features. Default value:
("discovery_auth", "acls", "acls_auth", "nps")
example: features = ("discovery_auth", "acls", "acls_auth")
example: features = () # no features supported

Detail of features:

  * tpgts
  The target fabric module is using iSCSI-style target portal group tags.

  * discovery_auth
  The target fabric module supports a fabric-wide authentication for
  discovery.

  * acls
  The target's TPGTs support explicit initiator ACLs.

  * acls_auth
  The target's TPGT's ACLs support per-ACL initiator authentication.

  * nps
  The TPGTs support iSCSI-like IPv4/IPv6 network portals, using IP:PORT
  group names.

  * nexus
  The TPGTs have a 'nexus' attribute that contains the local initiator
  serial unit. This attribute must be set before being able to create any
  LUNs.

  * wwn_types
  Sets the type of WWN expected by the target fabric. Defaults to 'free'.
  Usually a fabric will only support one type but iSCSI supports more.
  First entry is the "native" wwn type - i.e. if a wwn can be generated, it
  will be of this type.
  Example: wwn_types = ("eui",)
  Current valid types are:

    * free
    Freeform WWN.

    * iqn
    The fabric module targets are using iSCSI-type IQNs.

    * naa
    NAA FC or SAS address type WWN.

    * eui
    EUI-64. See http://en.wikipedia.org/wiki/MAC_address for info on this format.

    * unit_serial
    Disk-type unit serial.

* wwns
This property returns an iterable (either generator or list) of valid
target WWNs for the fabric, if WWNs should be chosen from existing
fabric interfaces. The most common case for this is hardware-set
WWNs. WWNs should conform to rtslib's normalized internal format: the wwn
type (see above), a period, then the wwn with interstitial dividers like
':' removed.

* to_fabric_wwn()
Converts WWNs from normalized format (see above) to whatever the kernel code
expects when getting a wwn. Only needed if different from normalized format.

* kernel_module
Sets the name of the kernel module implementing the fabric modules. If
not specified, it will be assumed to be MODNAME_target_mod, where
MODNAME is the name of the fabric module, from the fabrics list. Note
that you must not specify any .ko or such extension here.
Example: kernel_module = "my_module"

* configfs_group
Sets the name of the configfs group used by the fabric module. Defaults to the
name of the module from the fabrics list.
Example: configfs_group = "iscsi"

'''

import os
from glob import iglob as glob

from node import CFSNode
from utils import fread, fwrite, generate_wwn, normalize_wwn, colonize
from utils import RTSLibError, modprobe
from target import Target

version_attributes = set(["lio_version", "version"])
discovery_auth_attributes = set(["discovery_auth"])
target_names_excludes = version_attributes | discovery_auth_attributes

class _BaseFabricModule(CFSNode):
    '''
    Abstract Base clase for Fabric Modules.
    It can load modules, provide information about them and
    handle the configfs housekeeping. After instantiation, whether or
    not the fabric module is loaded depends on if a method requiring
    it (i.e. accessing configfs) is used. This helps limit loaded
    kernel modules to just the fabrics in use.
    '''

    # FabricModule ABC private stuff
    def __init__(self, name):
        '''
        Instantiate a FabricModule object, according to the provided name.
        @param name: the name of the FabricModule object. It must match an
        existing target fabric module specfile (name.spec).
        @type name: str
        '''
        super(_BaseFabricModule, self).__init__()
        self.name = str(name)
        self.spec_file = "N/A"
        self._path = "%s/%s" % (self.configfs_dir, self.name)
        self.features = ('discovery_auth', 'acls', 'acls_auth', 'nps', 'tpgts')
        self.wwn_types = ('free',)
        self.kernel_module = "%s_target_mod" % self.name

    # FabricModule public stuff

    def _check_self(self):
        if not self.exists:
            modprobe(self.kernel_module)
            self._create_in_cfs_ine('any')
        super(_BaseFabricModule, self)._check_self()

    def has_feature(self, feature):
        return feature in self.features

    def _list_targets(self):
        if self.exists:
            for wwn in os.listdir(self.path):
                if os.path.isdir("%s/%s" % (self.path, wwn)) and \
                        wwn not in target_names_excludes:
                    yield Target(self, wwn, 'lookup')

    def _get_version(self):
        if self.exists:
            for attr in self.version_attributes:
                path = "%s/%s" % (self.path, attr)
                if os.path.isfile(path):
                    return fread(path)
            else:
                raise RTSLibError("Can't find version for fabric module %s."
                                  % self.name)
        else:
            return None

    def to_normalized_wwn(self, wwn):
        '''
        Checks whether or not the provided WWN is valid for this fabric module
        according to the spec, and returns a tuple of our preferred string 
        representation of the wwn, and what type it turned out to be.
        '''
        return normalize_wwn(self.wwn_types, wwn, self.wwns)

    def to_fabric_wwn(self, wwn_type, wwn):
        '''
        Some fabrics need WWNs in a format different than rtslib's internal
        format. These fabrics should override this method.
        '''
        return wwn

    def needs_wwn(self):
        '''
        This fabric requires wwn to be specified when creating a target,
        it cannot be autogenerated.
        '''
        return self.wwns != None

    def _assert_feature(self, feature):
        if not self.has_feature(feature):
            raise RTSLibError("This fabric module does not implement "
                              + "the %s feature." % feature)

    def clear_discovery_auth_settings(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        self.discovery_mutual_password = ''
        self.discovery_mutual_userid = ''
        self.discovery_password = ''
        self.discovery_userid = ''
        self.discovery_enable_auth = False

    def _get_discovery_mutual_password(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/password_mutual" % self.path
        value = fread(path)
        if value == "NULL":
            return ''
        else:
            return value

    def _set_discovery_mutual_password(self, password):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/password_mutual" % self.path
        if password.strip() == '':
            password = "NULL"
        fwrite(path, "%s" % password)

    def _get_discovery_mutual_userid(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/userid_mutual" % self.path
        value = fread(path)
        if value == "NULL":
            return ''
        else:
            return value

    def _set_discovery_mutual_userid(self, userid):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/userid_mutual" % self.path
        if userid.strip() == '':
            userid = "NULL"
        fwrite(path, "%s" % userid)

    def _get_discovery_password(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/password" % self.path
        value = fread(path)
        if value == "NULL":
            return ''
        else:
            return value

    def _set_discovery_password(self, password):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/password" % self.path
        if password.strip() == '':
            password = "NULL"
        fwrite(path, "%s" % password)

    def _get_discovery_userid(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/userid" % self.path
        value = fread(path)
        if value == "NULL":
            return ''
        else:
            return value

    def _set_discovery_userid(self, userid):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/userid" % self.path
        if userid.strip() == '':
            userid = "NULL"
        fwrite(path, "%s" % userid)

    def _get_discovery_enable_auth(self):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/enforce_discovery_auth" % self.path
        value = fread(path)
        return int(value)

    def _set_discovery_enable_auth(self, enable):
        self._check_self()
        self._assert_feature('discovery_auth')
        path = "%s/discovery_auth/enforce_discovery_auth" % self.path
        if int(enable):
            enable = 1
        else:
            enable = 0
        fwrite(path, "%s" % enable)

    def _get_wwns(self):
        '''
        Returns either iterable or None. None means fabric allows
        arbitrary WWNs.
        '''
        return None

    discovery_userid = \
            property(_get_discovery_userid,
                     _set_discovery_userid,
                     doc="Set or get the initiator discovery userid.")
    discovery_password = \
            property(_get_discovery_password,
                     _set_discovery_password,
                     doc="Set or get the initiator discovery password.")
    discovery_mutual_userid = \
            property(_get_discovery_mutual_userid,
                     _set_discovery_mutual_userid,
                     doc="Set or get the mutual discovery userid.")
    discovery_mutual_password = \
            property(_get_discovery_mutual_password,
                     _set_discovery_mutual_password,
                     doc="Set or get the mutual discovery password.")
    discovery_enable_auth = \
            property(_get_discovery_enable_auth,
                     _set_discovery_enable_auth,
                     doc="Set or get the discovery enable_auth flag.")

    targets = property(_list_targets,
                       doc="Get the list of target objects.")

    version = property(_get_version,
                       doc="Get the fabric module version string.")

    wwns = property(_get_wwns,
                    doc="iterable of WWNs present for this fabric")

    def setup(self, fm, err_func):
        '''
        Setup fabricmodule with settings from fm dict.
        '''
        for name, value in fm.iteritems():
            if name != 'name':
                try:
                    setattr(self, name, value)
                except:
                    err_func("Could not set fabric %s attribute '%s'" % (fm['name'], name))

    def dump(self):
        d = super(_BaseFabricModule, self).dump()
        d['name'] = self.name
        for attr in ("userid", "password", "mutual_userid", "mutual_password"):
            val = getattr(self, "discovery_" + attr, None)
            if val:
                d["discovery_" + attr] = val
        d['discovery_enable_auth'] = bool(int(self.discovery_enable_auth))
        return d


class ISCSIFabricModule(_BaseFabricModule):

    def __init__(self):
        super(ISCSIFabricModule, self).__init__('iscsi')
        self.wwn_types = ('iqn', 'naa', 'eui')


class LoopbackFabricModule(_BaseFabricModule):
    def __init__(self):
        super(LoopbackFabricModule, self).__init__('loopback')
        self.features = ("nexus",)
        self.wwn_types = ('naa',)
        self.kernel_module = "tcm_loop"


class SBPFabricModule(_BaseFabricModule):
    def __init__(self):
        super(SBPFabricModule, self).__init__('sbp')
        self.features = ()
        self.wwn_types = ('eui',)
        self.kernel_module = "sbp_target"

    def to_fabric_wwn(self, wwn_type, wwn):
        # strip 'eui.'
        return wwn[4:]

    # return 1st local guid (is unique) so our share is named uniquely
    @property
    def wwns(self):
        for fname in glob("/sys/bus/firewire/devices/fw*/is_local"):
            if bool(int(fread(fname))):
                guid_path = os.path.dirname(fname) + "/guid"
                yield "eui." + fread(guid_path)[2:]
                break


class Qla2xxxFabricModule(_BaseFabricModule):
    def __init__(self):
        super(Qla2xxxFabricModule, self).__init__('qla2xxx')
        self.features = ("acls",)
        self.wwn_types = ('naa',)
        self.kernel_module = "tcm_qla2xxx"

    def to_fabric_wwn(self, wwn_type, wwn):
        # strip 'naa.' and add colons
        return colonize(wwn[4:])

    @property
    def wwns(self):
        for wwn_file in glob("/sys/class/fc_host/host*/port_name"):
            yield "naa." + fread(wwn_file)[2:]


class SRPTFabricModule(_BaseFabricModule):
    def __init__(self):
        super(SRPTFabricModule, self).__init__('ib_srpt')
        self.features = ("acls",)
        self.wwn_types = ('eui',)
        self.kernel_module = "ib_srpt"

    def to_fabric_wwn(self, wwn_type, wwn):
        # strip 'naa.'
        return "0xfe80000000000000" + wwn[4:]

    # Transform 'fe80:0000:0000:0000:0002:1903:000e:8acd' WWN notation to
    # 'eui.0002c903000e8acd'
    @property
    def wwns(self):
        for wwn_file in glob("/sys/class/infiniband/*/ports/*/gids/0"):
            yield "eui." + fread(wwn_file).translate(None, ":")[-16:]


class FCoEFabricModule(_BaseFabricModule):
    def __init__(self):
        super(FCoEFabricModule, self).__init__('tcm_fc')

        self.features = ("acls",)
        self.kernel_module = "tcm_fc"
        self.configfs_group = "fc"
        self.wwn_types=('naa',)

    def to_fabric_wwn(self, wwn_type, wwn):
        # strip 'naa.' and add colons
        return colonize(wwn[4:])

    @property
    def wwns(self):
        for wwn_file in glob("/sys/class/fc_host/host*/port_name"):
            yield "naa." + fread(wwn_file)[2:]


class USBGadgetFabricModule(_BaseFabricModule):
    def __init__(self):
        super(USBGadgetFabricModule, self).__init__('usb_gadget')
        self.features = ("nexus",)
        self.wwn_types = ('naa',)
        self.kernel_module = "tcm_usb_gadget"

    def to_fabric_wwn(self, wwn_type, wwn):
        # strip 'naa.'
        return wwn[4:]


class VhostFabricModule(_BaseFabricModule):
    def __init__(self):
        super(VhostFabricModule, self).__init__('vhost')
        self.features = ("nexus", "acls")
        self.wwn_types = ('naa',)
        self.kernel_module = "tcm_vhost"


fabric_modules = {
    "ib_srpt": SRPTFabricModule,
    "iscsi": ISCSIFabricModule,
    "loopback": LoopbackFabricModule,
    "qla2xxx": Qla2xxxFabricModule,
    "sbp": SBPFabricModule,
    "tcm_fc": FCoEFabricModule,
#    "usb_gadget": USBGadgetFabricModule, # very rare, don't show
    "vhost": VhostFabricModule,
    }

#
# Maintain compatibility with existing FabricModule(fabricname) usage
# e.g. FabricModule('iscsi') returns an ISCSIFabricModule
#
class FabricModule(object):

    def __new__(cls, name):
        return fabric_modules[name]()

    @classmethod
    def all(cls):
        for mod in fabric_modules.itervalues():
            yield mod()
