import raspberry_case
from solid import *
from solid.utils import *  # Not required, but the utils module is useful

import robothead_mount

SEGMENTS = 100

BASE_Y_LEN=58
PLATE_WIDTH=2
FRONT_X_SHIFT=25
BACK_X_SHIFT=15
BASE_X_LEN=65
SUPPORT_X_LEN=BASE_X_LEN - FRONT_X_SHIFT - BACK_X_SHIFT

REINFORCE_WIDTH=5

RASP_PLATE_HEIGHT=28
RASP_PLATE_X_SHIFT=20

SERVO_HEAD_DIAMETER = 24.5 # 24.5
SERVO_HEAD_DIAMETER_MARGIN = 3.5
HOLE_FRONT_X_SHIFT=16.5
HOLE_FRONT_Y_SHIFT=10
HOLE_BACK_X_SHIFT=32.5
HOLE_BACK_Y_SHIFT=10
HOLE_RADIUS=1.75
RASP_HOLE_X_SHIFT=40
RASP_HOLE_Y_SHIFT=15
RASP_HOLE_RADIUS=1.75


def parallelogram(w,h, skew, plate_width):
  return linear_extrude(height = plate_width)(
      polygon(points=[[0,0], [w,0], [w + skew, h], [skew,h], [0,0]], paths=[[0,1,2,3]])
  )


def y_symetry(obj):
  return scale([1,-1,1])(obj)

RASP_FIX_PLATE_WIDTH=3

def head_mount():
  base = left(FRONT_X_SHIFT)(forward(-BASE_Y_LEN / 2.0)
                             (cube([BASE_X_LEN, BASE_Y_LEN, PLATE_WIDTH])))

  p = parallelogram(SUPPORT_X_LEN,
                    RASP_PLATE_HEIGHT,
                    RASP_PLATE_X_SHIFT,
                    PLATE_WIDTH)
  p = rotate([90,0,0]) (p)
  
  rear_reinforce_l = back(BASE_Y_LEN / 2.0) (p)

  p2 = parallelogram(SUPPORT_X_LEN,
                     RASP_PLATE_HEIGHT / 4.0,
                     RASP_PLATE_X_SHIFT / 4.0,
                     BASE_Y_LEN)
  p2 = rotate([90,0,0]) (p2)
  rear_reinforce_base = p2
  rear_reinforce_base = forward(BASE_Y_LEN / 2.0)(rear_reinforce_base)

  p3 = parallelogram(SUPPORT_X_LEN,
                     RASP_PLATE_HEIGHT / 3.9,
                     RASP_PLATE_X_SHIFT / 3.9,
                     BASE_Y_LEN - REINFORCE_WIDTH * 2.0)
  p3 = rotate([90,0,0])(p3)
  rear_reinforce_base -= forward(BASE_Y_LEN / 2.0 - REINFORCE_WIDTH)(left(REINFORCE_WIDTH)(p3))
    
  rear_reinforce = rear_reinforce_l + y_symetry(rear_reinforce_l)

  rear_reinforce = right(BACK_X_SHIFT)(rear_reinforce + rear_reinforce_base)

  rasp_plate = right(BACK_X_SHIFT + RASP_PLATE_X_SHIFT)(forward(-BASE_Y_LEN / 2.0 - PLATE_WIDTH)
                                   (cube([SUPPORT_X_LEN, BASE_Y_LEN + 2 * PLATE_WIDTH, PLATE_WIDTH])))

  rasp_plate = up(RASP_PLATE_HEIGHT)(rasp_plate)

  

#  rasp_plate = up(PLATE_WIDTH)
  

  servo_hole = translate([0,0, 5]) (
    cylinder(r = (SERVO_HEAD_DIAMETER + SERVO_HEAD_DIAMETER_MARGIN)/ 2.0, h = 100, center = True)
    )

  front_hole_a = translate([-HOLE_FRONT_X_SHIFT,0, 5]) (
        cylinder(r = HOLE_RADIUS, h = 100, center = True)
    )
  front_hole_b = translate([-HOLE_FRONT_X_SHIFT,HOLE_FRONT_Y_SHIFT, 5]) (
        cylinder(r = HOLE_RADIUS, h = 100, center = True)
    )

  back_hole_a = translate([HOLE_BACK_X_SHIFT,0, 5]) (
        cylinder(r = HOLE_RADIUS, h = 20, center = True)
    )
  back_hole_b = translate([HOLE_BACK_X_SHIFT,HOLE_BACK_Y_SHIFT, 5]) (
        cylinder(r = HOLE_RADIUS, h = 20, center = True)
    )

  rasp_hole_a = translate([RASP_HOLE_X_SHIFT, -RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    )

  rasp_hole_b = translate([RASP_HOLE_X_SHIFT, RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    )


  rasp_hole_c = translate([RASP_HOLE_X_SHIFT + 15, -RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    )

  rasp_hole_d = translate([RASP_HOLE_X_SHIFT + 15, RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    )


  head_mount = base + rear_reinforce + rasp_plate
    
  return head_mount - hole()(front_hole_a + front_hole_b + servo_hole + back_hole_a + back_hole_b + rasp_hole_a + rasp_hole_b + rasp_hole_c + rasp_hole_d)


if __name__ == '__main__':
    a = head_mount()
    scad_render_to_file( a, "robot_head_mount_2.scad", file_header='$fn = %s;' % SEGMENTS)
  
