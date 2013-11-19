# -*- coding: utf-8 -*-
"""Manage MLS frontend components like web server, load balancer and cache."""

from fabric import api


@api.task
@api.roles('frontend')
def restart():
    """Restart the frontend components."""
    restart_haproxy()
    restart_varnish()
    restart_nginx()


@api.task
@api.roles('frontend')
def restart_nginx():
    """Restart the NginX web server component."""
    api.sudo('/etc/init.d/nginx restart')


@api.task
@api.roles('frontend')
def restart_varnish():
    """Restart the Varnish caching proxy component."""
    api.sudo('/etc/init.d/varnish restart')


@api.task
@api.roles('frontend')
def restart_haproxy():
    """Restart the HA-Proxy load balancer component."""
    api.sudo('/etc/init.d/haproxy restart')
