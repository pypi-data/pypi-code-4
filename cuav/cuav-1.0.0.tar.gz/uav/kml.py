#!/usr/bin/env python

'''
create a kml file
'''

class kml(object):
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, mode='w')
        self.f.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>Joe-Matt</name>
	<Style id="default+icon=http://maps.google.com/mapfiles/kml/pal3/icon60.png">
		<IconStyle>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pal3/icon60.png</href>
			</Icon>
		</IconStyle>
	</Style>
	<StyleMap id="default+nicon=http://maps.google.com/mapfiles/kml/pal3/icon60.png+hicon=http://maps.google.com/mapfiles/kml/pal3/icon52.png">
		<Pair>
			<key>normal</key>
			<styleUrl>#default+icon=http://maps.google.com/mapfiles/kml/pal3/icon60.png</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#default+icon=http://maps.google.com/mapfiles/kml/pal3/icon52.png</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="default+icon=http://maps.google.com/mapfiles/kml/pal3/icon52.png">
		<IconStyle>
			<scale>1.1</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pal3/icon52.png</href>
			</Icon>
		</IconStyle>
		<LabelStyle>
			<scale>1.1</scale>
		</LabelStyle>
	</Style>
''')

    def add_point(self, name, lat, lon):
        self.f.write('''<Placemark>
		<name>%s</name>
		<Point>
			<coordinates>%f,%f,0</coordinates>
		</Point>
	</Placemark>
''' % (name, lon, lat))

    def close(self):
        self.f.write('''</Document>
</kml>
''')
        self.f.close()
