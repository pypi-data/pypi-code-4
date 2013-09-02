import raspberry_case
from solid import *
from solid.utils import *  # Not required, but the utils module is useful

SEGMENTS = 40


FRONT_WIDTH=56
PLATE_WIDTH=2
FRONT_X_SHIFT=25
FRONT_BACK_SHIFT=15
FRONT_LENGTH=60
RASP_PLATE_HEIGHT=20

SERVO_HEAD_DIAMETER = 26 # 24.5
HOLE_FRONT_X_SHIFT=16.5
HOLE_FRONT_Y_SHIFT=10
HOLE_BACK_X_SHIFT=32.5
HOLE_BACK_Y_SHIFT=10
HOLE_RADIUS=1.5
RASP_HOLE_X_SHIFT=40
RASP_HOLE_Y_SHIFT=15
RASP_HOLE_RADIUS=1.5

MARGIN = 1

def parallelogram(w,h, skew, plate_width):
  return linear_extrude(height = plate_width)(
      polygon(points=[[0,0], [w,0], [w + skew, h], [skew,h], [0,0]], paths=[[0,1,2,3]])
  )

RASP_FIX_PLATE_WIDTH=3

def head_mount():       
  head_mount = union() (
      translate([-FRONT_X_SHIFT,-FRONT_WIDTH / 2,0]) (
        cube([FRONT_LENGTH + 5, FRONT_WIDTH, PLATE_WIDTH])
      ),

       translate([FRONT_BACK_SHIFT, -FRONT_WIDTH / 2, 0]) (
         rotate([90,0,0]) (
            parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,RASP_PLATE_HEIGHT, RASP_PLATE_HEIGHT, PLATE_WIDTH)
         )
       ),

      translate([FRONT_BACK_SHIFT,0,0]) (
        translate([0, FRONT_WIDTH / 2 - 0.001 + PLATE_WIDTH, 0])  (
          rotate([90,0,0]) (
             parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,RASP_PLATE_HEIGHT, RASP_PLATE_HEIGHT, PLATE_WIDTH)
          )
        )
      ),

      translate([FRONT_BACK_SHIFT + 25, -FRONT_WIDTH / 2, 0]) (
        rotate([-90,0,0]) (
          parallelogram(FRONT_LENGTH - 40 - FRONT_X_SHIFT,-5,5, FRONT_WIDTH)
        )
      ),

      translate([FRONT_BACK_SHIFT, -FRONT_WIDTH / 2, 0]) (
        rotate([-90,0,0]) (
          parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,-5,5, 5)
        )
      ),

      translate([FRONT_BACK_SHIFT, FRONT_WIDTH / 2 - 5, 0]) (
        rotate([-90,0,0]) (
          parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,-5,5, 5)
        )
      ),

      translate([RASP_PLATE_HEIGHT - RASP_FIX_PLATE_WIDTH + FRONT_BACK_SHIFT, -FRONT_WIDTH / 2, RASP_PLATE_HEIGHT - RASP_FIX_PLATE_WIDTH]) (
        rotate([-90,0,0]) (
          parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,-RASP_FIX_PLATE_WIDTH,RASP_FIX_PLATE_WIDTH, 10)
        )
      ),

      translate([RASP_PLATE_HEIGHT - RASP_FIX_PLATE_WIDTH + FRONT_BACK_SHIFT, FRONT_WIDTH / 2 - 10, RASP_PLATE_HEIGHT - RASP_FIX_PLATE_WIDTH]) (
        rotate([-90,0,0]) (
          parallelogram(FRONT_LENGTH - 10 - FRONT_X_SHIFT,-RASP_FIX_PLATE_WIDTH,RASP_FIX_PLATE_WIDTH, 10)
        )
      )
  )

  servo_hole = translate([0,0, 5]) (
    cylinder(r = SERVO_HEAD_DIAMETER / 2.0 + MARGIN / 2, h = 100, center = True)
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


  
  return head_mount - hole()(front_hole_a + front_hole_b + servo_hole + back_hole_a + back_hole_b + rasp_hole_a + rasp_hole_b + rasp_hole_c + rasp_hole_d)


if __name__ == '__main__':
    a = head_mount()
    scad_render_to_file( a, "robot_head_mount.scad", file_header='$fn = %s;' % SEGMENTS)
  
