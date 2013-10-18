import unittest
import xml.etree.ElementTree as ET
import node

class NodeTestCases(unittest.TestCase):
    def test_simple_text_value(self):
        n = node.Node(make_simple_xml_element())
        self.assertEquals(n.guidata.skin.scoreFontName, "Tahoma Bold")


    def test_second_text_value(self):
        n = node.Node(make_simple_xml_element())
        self.assertEquals(n.guidata.skin.backgroundFile, '"back.bmp"')

    def test_repeated_elements(self):
        n = node.Node(make_simple_xml_element())
        self.assertEquals(type(n.guidata.skin.nextBlockX.line),  tuple)
        self.assertEquals(n.guidata.skin.nextBlockX.line[3], "No A Number" )

    def test_convert_to_int(self):
        n = node.Node(make_simple_xml_element())
        self.assertEquals(n.guidata.skin.nextBlockX.line[1], 206 )

    def test_does_not_convert_floats_or_decimals(self):
        n = node.Node(make_simple_xml_element())
        self.assertEquals(n.guidata.skin.nextBlockX.line[2], "207.5")

    def test_tuple_of_nodes(self):
        n = node.Node(make_menu_element())
        self.assertEquals(type(n.breakfast_menu.food),  tuple)
        self.assertEquals(n.breakfast_menu.food[1].name, "Strawberry Belgian Waffles" )

    def test_iterate_over_nodes(self):
        n = node.Node(make_menu_element())
        for i, food in enumerate(n.breakfast_menu.food):
            self.assertEquals(type(food), node.Node)
            self.assertEquals(type(food.name), str)

        self.assertEquals(i, 4)



    def test_attribute_access(self):
        n = node.Node(make_config_element())
        self.assertEquals(type(n.configuration.email),  tuple)
        self.assertEquals(type(n.configuration.phone),  tuple)
        self.assertEquals(n.configuration.email[0],"jdoe@company.dom")
        self.assertEquals(type(n.configuration.phone[0]),node.Node)
        self.assertEquals(n.configuration.phone[0].text,"555-555-1111")
        self.assertEquals(n.configuration.phone[0].type,"home")

def make_simple_xml_element():
    et = ET.fromstring("""\
<?xml version="1.0"?>
<guidata>
    <skin>
        <scoreFontName>Tahoma Bold</scoreFontName>
        <scoreFontHeight>20</scoreFontHeight>
        <blockSize>16</blockSize>
        <nextBlockX>
            <line>205</line>
            <line>206</line>
            <line>207.5</line>
            <line>No A Number</line>
        </nextBlockX>
        <backgroundFile>"back.bmp"</backgroundFile>
    </skin>
</guidata>
""")
    return et

def make_menu_element():
    et = ET.fromstring("""\
<?xml version="1.0" encoding="ISO-8859-1"?>
<breakfast_menu>
	<food>
		<name>Belgian Waffles</name>
		<price>$5.95</price>
		<description>Two of our famous Belgian Waffles with plenty of real maple syrup</description>
		<calories>650</calories>
	</food>
	<food>
		<name>Strawberry Belgian Waffles</name>
		<price>$7.95</price>
		<description>Light Belgian waffles covered with strawberries and whipped cream</description>
		<calories>900</calories>
	</food>
	<food>
		<name>Berry-Berry Belgian Waffles</name>
		<price>$8.95</price>
		<description>Light Belgian waffles covered with an assortment of fresh berries and whipped cream</description>
		<calories>900</calories>
	</food>
	<food>
		<name>French Toast</name>
		<price>$4.50</price>
		<description>Thick slices made from our homemade sourdough bread</description>
		<calories>600</calories>
	</food>
	<food>
		<name>Homestyle Breakfast</name>
		<price>$6.95</price>
		<description>Two eggs, bacon or sausage, toast, and our ever-popular hash browns</description>
		<calories>950</calories>
	</food>
</breakfast_menu>
""")
    return et




def make_config_element():
    et = ET.fromstring("""\
<?xml version="1.0" encoding="ISO-8859-1"?>
<configuration>
    <email>jdoe@company.dom</email>
    <email>jdoe@personal.dom</email>
    <phone type="home">555-555-1111</phone>
    <phone type="cell">555-555-2222</phone>
    <login id="jdoe" pass="mypass" />
</configuration> 
""")
    return et
