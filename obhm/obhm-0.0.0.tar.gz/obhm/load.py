def are_we_overloaded():
    cpus = open("/proc/cpuinfo").read().count("processor\t:")
    loadavg = float(open("/proc/loadavg").read().split()[0])
    return loadavg > cpus
