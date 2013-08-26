# -*- coding: utf-8 -*-
"""
``pybill.lib.config.register`` module defines the class that manages the
various configuration objects used during a PyBill run.

This class is the only public class of the ``pybill.lib.config`` package and
should be the only one used outside this package.

.. autoclass:: ConfigRegister
   :members:
   :undoc-members:
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"

import os
from os import path as osp

from pybill.lib.config.entities import ConfigData
from pybill.lib.config.xmlreaders import load_config


class ConfigRegister:
    """
    Class containing the various configuration objects read by PyBill.

    A configuration object is an instance of
    :class:`~pybill.lib.config.entities.ConfigData` class.  This register is
    used to get the correct configuration specified by an accounting document in
    its processing instruction. The register is also responsible for finding the
    configuration files and storing them after indexing them with their file
    name.

    Basically, the configuration files can be found in three places:

    - specified on the command-line (they are then stored in any directory),

    - specified in the processing instruction inside an accounting document and
      stored in the user configuration directory (\ ``~/.config/pybill/``\ ),

    - specified in the processing instruction inside an accounting document and
      stored in the system configuration directory
      (\ ``/etc/pybill/config/``\ ).

    .. attribute:: configs

        Attribute containing a dictionary that stores the configuration objects
        read from the disk, indexed by their reference.

        type: dictionary of :class:`~pybill.lib.config.entities.ConfigData`
              indexed with :class:`unicode` keys

    .. data:: SYSTEM_CONFIG_DIR

       Class constant containing the name of the system directory that contains
       the PyBill config files. Is currently u"/etc/pybill/config/".

       type: :class:`unicode`

    .. attribute:: USER_CONFIG_DIR

       Class constant containing the name of the user directory that contains
       the PyBill config files. Is currently u"~/.config/pybill/".

       type: :class:`unicode`

    .. attribute:: DEFAULT_CONFIG_REF

       Class constant containing the reference of the default
       configuration. This reference is the name of the file that contains this
       configuration. Is currently u"default".

       type: :class:`unicode`

    .. automethod:: __init__
    """
    SYSTEM_CONFIG_DIR = u"/etc/pybill/config/"
    USER_CONFIG_DIR = u"~/.config/pybill/"
    DEFAULT_CONFIG_REF = u"default"
    def __init__(self):
        """
        Intializes a new object.

        Actually there is only one single object for PyBill that manages the
        configurations.
        """
        self.configs = {}
        # Loads default config
        default_file = self.find_config_file(self.__class__.DEFAULT_CONFIG_REF)
        if default_file is None:
            self.configs[self.__class__.DEFAULT_CONFIG_REF] = ConfigData()
        else:
            self.store_config(self.__class__.DEFAULT_CONFIG_REF, default_file)

    def find_config_file(self, config_ref):
        """
        Finds the file containing the configuration whose name is
        ``config_ref``.

        ``config_ref`` can directly be a file or can be a reference to a file
        located in ``~/.config/pybill/`` or in ``/etc/pybill/config/``. In that
        last case, the file name is ``{config_ref}.xml``.

        If the file can't be found, returns None.

        :parameter config_ref: Reference of the configuration whose file must
                               be found.
        :type config_ref: :class:`unicode`

        :returns: The absolute path of the file containing the configuration
                  whose name is ``config_ref``. Returns ``None`` if the file
                  can't be found.
        :rtype: :class:`unicode`
        """
        if config_ref is not None and osp.exists(config_ref):
            return osp.abspath(config_ref)
        cfg_filename = u"%s.xml" % config_ref
        user_dir = osp.expanduser(self.__class__.USER_CONFIG_DIR)
        if osp.isdir(user_dir) and cfg_filename in os.listdir(user_dir):
            return unicode(osp.join(user_dir, cfg_filename))
        if (osp.isdir(self.__class__.SYSTEM_CONFIG_DIR)
            and cfg_filename in os.listdir(self.__class__.SYSTEM_CONFIG_DIR)):
            return unicode(osp.join(self.__class__.SYSTEM_CONFIG_DIR,
                                    cfg_filename))
        return None

    def store_config(self, config_ref, config_filename):
        """
        Stores a new configuration associated to the reference ``config_ref``.
        
        This configuration is described in the file ``config_filename`` and
        therefore must be read and stored in a ``ConfigData`` object before
        being stored in this object.

        :parameter config_ref: reference of the configuration that will be
                               added in this object.
        :type config_ref: :class:`unicode`

        :parameter config_filename: Absolute path of the file containing the
                                    configuration that will be added in this
                                    object.
        :type config_filename: :class:`unicode`
        """
        config = load_config(config_filename)
        config.reference = config_ref
        self.configs[config_ref] = config
    
    def get_config(self, config_ref):
        """
        Gets the configuration whose reference is ``config_ref``.

        If this configuration has already been read and is stored inside this
        object, directly returns it. Else, tries to find the file containing the
        desired configuration, reads it, stores it for further uses and returns
        it.

        :parameter config_ref: Reference of the desired configuration.
        :type config_ref: :class:`unicode`

        :returns: Configuration object whose name is ``config_ref``.
        :rtype: :class:`~pybill.lib.config.entities.ConfigData`
        """
        if config_ref not in self.configs:
            config_filename = self.find_config_file(config_ref)
            if config_filename is None:
                return self.configs[u"default"]
            else:
                self.store_config(config_ref, config_filename)
        return self.configs[config_ref]
