#!/usr/bin/env python
# coding=utf-8
import pkg_resources
pkg_resources.declare_namespace(__name__)
version = pkg_resources.require('graf')[0].version

def use(environment):
    from graf.plugins import registry
    environment.update(registry.raw)
