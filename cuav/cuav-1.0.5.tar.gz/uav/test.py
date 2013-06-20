#!/usr/bin/env python
'''
convert roll, pitch, yaw to x, y, z components and back again

'''

import math

def RPY_to_XYZ(roll, pitch, yaw, length):
    '''convert roll, pitch and yaw in degrees to
       components in X, Y and Z

       inputs:
       
       roll, pitch and yaw are in degrees
       yaw == 0 when pointing North
       roll == zero when horizontal. +ve roll means tilting to the right
       pitch == zero when horizontal, +ve pitch means nose is pointing upwards
       length is in an arbitrary linear unit.
       When RPY is (0, 0, 0) then length represents distance upwards

       outputs:
       X is in units along latitude. +ve X means going North
       Y is in units along longitude +ve Y means going East
       Z is altitude in units (+ve is up)
       '''
    import euclid
    q = euclid.Quaternion.new_rotate_euler(-math.radians(pitch),
                                           math.radians(yaw),
                                           -math.radians(roll))
    v = euclid.Vector3(0, 0, length)
    v2 = q * v
    return (v2.x, v2.y, v2.z)

if __name__ == '__main__':

    def test(roll, pitch, yaw, length):
        (x, y, z) = RPY_to_XYZ(roll, pitch, yaw, length)
        l2 = math.sqrt(x*x + y*y + z*z)
        if math.fabs(length - l2) > 0.00001:
            raise RuntimeError("length error")
        print("roll=%f pitch=%f yaw=%f  =>  x=%f y=%f z=%f" % (
            roll, pitch, yaw,
            x, y, z))

    test(0, 0, 0, 1)
    test(90, 0, 0, 1)
    test(45, 0, 0, 1)

    test(0, 90, 0, 1)
    test(0, 45, 0, 1)

    test(0, 0, 90, 1)
    test(0, 0, 45, 1)

    test(45, 45, 0, 1)

    
