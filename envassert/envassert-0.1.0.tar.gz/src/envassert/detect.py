from __future__ import with_statement
from fabric.api import run, hide
from fabric.contrib.files import exists

# https://github.com/opscode/ohai/blob/master/lib/ohai/plugins/linux/platform.rb


def detect():
    detected_os = detect_os()
    if "linux" in detected_os:
        return linux()
    elif "freebsd" in detected_os:
        return "freebsd"
    elif "darwin" in detected_os:
        return "darwin"
    elif "netbsd" in detected_os:
        return "netbsd"
    elif "openbsd" in detected_os:
        return "openbsd"
    else:
        return None


def detect_os():
    with hide("everything"):
        return run('uname').lower()


def get_lsb():
    if exists("/etc/lsb-release"):
        for line in open("/etc/lsb-release").readline():
            if line.find("DISTRIB_ID"):
                return line.split("=")[1].lower()
    elif exists("/usr/bin/lsb_release"):
        with hide("everything"):
            ret = run("/usr/bin/lsb_release -a")
        for line in ret:
            if line.find("DISTRIB_ID"):
                return line.split("=")[1].lower()
    return None


def linux():
    lsb = get_lsb()

    if exists("/etc/oracle-release"):
        platform = "oracle"
    elif exists("/etc/enterprise-release"):
        platform = "oracle"
    elif exists("/etc/debian_version"):
        if lsb == "ubuntu":
            platform = "ubuntu"
        else:
            if exists("/usr/bin/raspi-config"):
                platform = "raspbian"
            else:
                platform = "debian"
    elif exists("/etc/redhat-release"):
        with hide("everything"):
            contents = run("cat /etc/redhat-release")
        platform = get_redhatish_platform(contents)
    elif exists("/etc/system-release"):
        with hide("everything"):
            contents = run("cat /etc/system-release")
        platform = get_redhatish_platform(contents)
    elif exists("/etc/gentoo-release"):
        platform = "gentoo"
    elif exists("/etc/SuSE-release"):
        platform = "suse"
    elif exists("/etc/slackware-version"):
        platform = "slackware"
    elif exists("/etc/arch-release"):
        platform = "arch"
    elif lsb == "redhat":
        platform = "redhat"
    elif lsb == "amazon":
        platform = "amazon"
    elif lsb == "ScientificSL":
        platform = "scientific"

    # platform_family
    if platform in ["debian", "ubuntu", "linuxmint", "raspbian"]:
        return "debian"
    elif platform in ["fedora"]:
        return "fedora"
    elif platform in ["oracle", "centos", "redhat", "scientific", "enterpriseenterprise", "amazon"]:
        return "rhel"
    elif platform in ["suse"]:
        return "suse"
    elif platform in ["gentoo"]:
        return "gentoo"
    elif platform in ["slackware"]:
        return "slackware"
    elif platform in ["arch"]:
        return "arch"


def get_redhatish_platform(contents):
    if "CentOS" in contents:
        return "centos"
    elif "Red Hat" in contents:
        return "redhat"
    else:
        return None
