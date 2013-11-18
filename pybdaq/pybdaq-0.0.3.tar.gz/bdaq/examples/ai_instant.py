import time
import plac
import bdaq


@plac.annotations()
def main(device_name="USB-4702, BID#0", start=0, count=1):
    # set up the device
    print "accessing device:", device_name

    instant_ai = bdaq.InstantAiCtrl()

    instant_ai.selected_device = bdaq.DeviceInformation(
        #description=device_name)
        number=0)

    # acquire data forever
    try:
        print "acquisition in progress"

        #count_max = instant_ai.features.channel_count_max
        count_max = 128

        while True:
            scaled_data = instant_ai.read_raw(start, count)

            for (i, value) in enumerate(scaled_data):
                print "channel {} data: {:10.6f}".format(
                    (i + start) % count_max,
                    value)

            print

            time.sleep(1.0)
    finally:
        instant_ai.dispose()


if __name__ == "__main__":
    plac.call(main)
