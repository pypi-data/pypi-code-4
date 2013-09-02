from solid import *
from solid.utils import *  # Not required, but the utils module is useful

SEGMENTS = 20

RASP_TOTAL_X=85.5
RASP_TOTAL_Y=57
RASP_TOTAL_Z=20

AIR_HOLE_NUMBER=6
AIR_HOLE_DIAMETER=2

BASE_PLATE_ENTRETOISE_RADIUS=3
RASP_HOLE_RADIUS=2.9 / 2.0
BASE_PLATE_HOLE_RADIUS=RASP_HOLE_RADIUS
ENTRETOISE_HEIGHT = 7
BASE_PLATE_ENTRETOISES = [[25.5,   18, ENTRETOISE_HEIGHT / 2.0],
                          [  25.5, 43.5, ENTRETOISE_HEIGHT / 2.0],
                          [  79, 43.5, ENTRETOISE_HEIGHT / 2.0],
                          [  77, 10, ENTRETOISE_HEIGHT / 2.0],
                          ]


CALE_HEIGHT=3
CALE_WIDTH=3
CALE_H_LENGTH=10
CALE_V_LENGTH=CALE_H_LENGTH + CALE_WIDTH
H_CALES = [[0, -CALE_WIDTH,0],
           [RASP_TOTAL_X - CALE_H_LENGTH, -CALE_WIDTH,0],
           [RASP_TOTAL_X - CALE_H_LENGTH, RASP_TOTAL_Y,0],
           [0, RASP_TOTAL_Y,0],
          ]

V_CALES = [[-CALE_WIDTH , RASP_TOTAL_Y - CALE_V_LENGTH + CALE_WIDTH,0],
           [RASP_TOTAL_X, RASP_TOTAL_Y - CALE_V_LENGTH + CALE_WIDTH,0],
          ]

HDMI_PORT_X_SHIFT = 45;
USB_PORT_Y_SHIFT = 30;
HDMI_HEIGHT = 15
USB_HEIGHT = 15

def cable_output():
   hdmi = translate([HDMI_PORT_X_SHIFT, -70, ENTRETOISE_HEIGHT + HDMI_HEIGHT / 2]) (
      cube([25,150, HDMI_HEIGHT], center = True)
   )
   usb = translate([170, USB_PORT_Y_SHIFT, ENTRETOISE_HEIGHT + USB_HEIGHT / 2])(
      cube([150,25, USB_HEIGHT], center = True)
   )
   return hdmi + usb


def entretoise (r_outer, r_inner, h, center = False):
  return cylinder(r=r_outer, h=h, center = center) - cylinder(r=r_inner, h=h * 2, center = center)

def air_holes():
  return translate([40,30, 0])(
      [
        rotate(i  * 360 / AIR_HOLE_NUMBER, [0, 0, 1])
        (
              translate([0, 10, 0])
              (
                  cylinder(r=AIR_HOLE_DIAMETER, h=10,  center = True)
              )
        )
        for i in range(6)
      ]
    )

def h_cale(i):
  return translate(i) (
    cube([CALE_H_LENGTH, CALE_WIDTH, ENTRETOISE_HEIGHT + CALE_HEIGHT], center = False)
  )


def v_cale(i):
  return translate(i) (
    cube([CALE_WIDTH, CALE_V_LENGTH, ENTRETOISE_HEIGHT + CALE_HEIGHT], center = False)
  )

def raspberry_case():
  holes = air_holes() + cable_output()
  entretoises = [translate(i)
                 (entretoise(BASE_PLATE_ENTRETOISE_RADIUS, BASE_PLATE_HOLE_RADIUS, h = ENTRETOISE_HEIGHT, center=True))
                 for i in BASE_PLATE_ENTRETOISES]

  h_cales = [h_cale(i) for i in H_CALES ]
  v_cales = [v_cale(i) for i in V_CALES ]

  return union()(entretoises + h_cales + v_cales) - hole()(holes)

if __name__ == '__main__':
    CASE_X_SIZE = 130
    case_width = 2
    outer_case  = cube([CASE_X_SIZE, 100, 40]) - translate([case_width,case_width,case_width])(cube([CASE_X_SIZE - case_width * 2, 100 - case_width * 2, 40]))
#    outer_case = minkowski()(outer_case, cylinder(r = 1, h = 1))
    a = outer_case + translate([20, 20])(rotate(0)(raspberry_case()))
    scad_render_to_file( a, "raspberry_py_case.scad", file_header='$fn = %s;' % SEGMENTS, include_orig_code=True)
