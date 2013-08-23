import hid
import time

devs = []
candidates = {(x['vendor_id'], x['product_id'])
              for x in hid.enumerate(0, 0)}
for cand in candidates:
    print "Trying to open {0}, {1}".format(*cand)
    dev = hid.device(*cand)
    dev.set_nonblocking(True)
    devs.append(dev)

while True:
    for dev in devs:
        # See if there's input
        if dev.read(8):
            # Wait for key release
            while not dev.read(8):
                time.sleep(0.01)
                continue
            print "Trigger pressed"
        else:
            time.sleep(0.01)
