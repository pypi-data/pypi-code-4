import serial
HIGH='HIGH'
LOW='LOW'
class ioStick:
     port="/dev/ttyS0"
     def __init__(self, serport="/dev/ttyACM0"):
          self.port=serport
          self.ser=serial.Serial(serport,4800)
     def digitalWrite(self,pin,status):
          x=convert(pin)
          y=x[0]+x[1]
          if(status == HIGH):
               self.ser.write("h"+y)
          else:
               self.ser.write("l"+y)
     def digitalRead(self,pin):
          x=convert(pin)
          y=x[0]+x[1]
          self.ser.write("r"+y)
          z=self.ser.read()
          if (z == '1'):
               return(HIGH)
          else:
               return(LOW)
def convert(numb):
     a=['0','1']
     if (numb <= 9):
             a[0]=str(numb)
             a[1]='0'
     else:
             a[0]='9'
             a[1]=str(numb-9)
     return a
