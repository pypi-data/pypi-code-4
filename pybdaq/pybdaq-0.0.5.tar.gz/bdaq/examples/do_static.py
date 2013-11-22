import bdaq


def main():
    # open the device
    instant_do = bdaq.InstantDoCtrl()

    instant_do.selected_device = bdaq.DeviceInformation(number=0)

    # write DO ports
    instant_do.write(0, [True])

    print "DO output completed!"

if __name__ == "__main__":
    main()
