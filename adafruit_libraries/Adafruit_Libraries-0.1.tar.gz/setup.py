from distutils.core import setup

setup(
	name='Adafruit_Libraries',
	version='0.1',
	author='Adafruit',
	packages=['Adafruit', 'Adafruit.ADS1x15', 'Adafruit.BMP085', 'Adafruit.CharLCD', 'Adafruit.CharLCDPlate', 'Adafruit.DHT_Driver', 'Adafruit.I2C', 'Adafruit.LEDBackpack', 'Adafruit.LEDpixels', 'Adafruit.LSM303', 'Adafruit.MCP230xx', 'Adafruit.MCP3008', 'Adafruit.MCP4725', 'Adafruit.PWM_Servo_Driver', 'Adafruit.TCS34725', 'Adafruit.VCNL4000'],
	url='http://www.adafruit.com/',
	license='LICENSE.txt',
	description='Libraries for using Adafruit Hardware on a Raspberry Pi or BeagleBone Black',
	long_description=open('README.md').read(),
)