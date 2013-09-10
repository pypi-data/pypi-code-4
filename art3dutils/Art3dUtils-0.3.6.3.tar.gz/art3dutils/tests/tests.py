# -*- coding: utf-8 -*-

import unittest
import json


from xml.dom.minidom import parseString
from ..models import (Project, Quarter, Building, Section, Floor, Apartment,
                      populate_session)
from ..utilities import get_polygon_nodes

session = populate_session('sqlite:///', True)

TEST_PDF = 'test.pdf'


class ModelTest(unittest.TestCase):

    def setUp(self):
        with open('json/canonic.json', 'r') as f:
            json_data = json.load(f)
            for apt_obj in json_data:
                Apartment.add('test', **apt_obj)
        session.commit()

    def tearDown(self):
        session.close()

    def test_project(self):
        project = Project.fetch('test')
        self.assertEqual('test', project.title)
        self.assertEqual(1, len(project.quarters))
        self.assertEqual(1, len(project.quarters[0].buildings))
        self.assertEqual(3, len(project.fetch_apartments()))

    def test_delete_project(self):
        project = Project.fetch('test')
        session.delete(project)
        session.commit()
        removed = Project.fetch('test')
        self.assertIsNone(removed)
        quarters = Quarter.fetch_all('test')
        self.assertEqual(0, len(quarters))
        buildings = Building.fetch_all('test')
        self.assertEqual(0, len(buildings))
        sections = Section.fetch_all('test')
        self.assertEqual(0, len(sections))
        floors = Floor.fetch_all('test')
        self.assertEqual(0, len(floors))
        apts = Apartment.fetch_all('test')
        self.assertEqual(0, len(apts))

    def test_quarter(self):
        quarter = session.query(Quarter).get(('test', 1))
        self.assertEqual(1, quarter.number)
        self.assertEqual(2, len(quarter.buildings))
        for building in quarter.buildings:
            self.assertEqual(quarter, building.quarter)
            if building.number is 1:
                self.assertEqual(2, len(building.sections))
                for section in building.sections:
                    if section.number is 1:
                        self.assertEqual(4, len(section.floors))
                        for floor in section.floors:
                            if floor.number is 3:
                                self.assertEqual(8, len(floor.apartments))
        self.assertEqual(1, len(quarter.fetch_available_buildings()))
        self.assertEqual(1, quarter.fetch_available_buildings()[0].number)

    def test_get_apartments(self):
        floor = Floor.fetch(('test', 1, 1, 1, 3))
        self.assertEqual(8, len(floor.apartments))
        self.assertEqual([8, 7, 6, 5, 4, 3, 2, 1],
                         [apt.number for apt in floor.fetch_apartments()])
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                         [apt.number for apt in floor.fetch_apartments(sort_key='number')])
        self.assertEqual([1, 3, 4, 5, 6, 7, 8],
                         [apt.number for apt in floor.fetch_apartments(
                             sort_key='number', available_only=True)])

    def test_add_apartment(self):
        new_apt = Apartment.add('test', 2, 1, 1, 1, 1)
        new_apt.square = 56.6
        quarters = Quarter.fetch_all()
        self.assertEqual(2, len(quarters))

        apt = Apartment.fetch(('test', 2, 1, 1, 1, 1))
        self.assertEqual(1, apt.pl)
        self.assertEqual(56.6, apt.square)

    def test_apartment_fetch_all(self):
        apartments1 = Apartment.fetch_all('test', 1, 1, 1, 1)
        self.assertEqual(0, len(apartments1))
        apartments3 = Apartment.fetch_all('test', 1, 1, 1, 3)
        self.assertEqual(8, len(apartments3))

    def test_get_center(self):
        apartment = Apartment.fetch_all('test', 1, 1, 1, 3, 1)[0]
        self.assertEqual((187.808, 177.3225), apartment.get_center())

    def test_area_coords(self):
        apartment = Apartment.fetch_all('test', 1, 1, 1, 3, 1)[0]
        self.assertEqual('283,2,283,185,222,185,222,224,166,224,'
                         '166,351,92,351,92,49,200,49,200,2,282,2,283,2',
                          apartment.area_coords())

    def test_render_svg(self):
        apartment = Apartment.fetch_all('test', 1, 1, 1, 3, 1)[0]
        self.assertEqual(
            '<?xml version="1.0" ?><!DOCTYPE svg  PUBLIC \'-//W3C//DTD '
            'SVG 1.1//EN\'  \'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\'>'
            '<svg enable-background="new 0.0 0.0                         '
            '770 425" height="425px" version="1.1" viewBox="0.0 0.0 770 425" '
            'width="770px" x="0px" xml:space="preserve" '
            'xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" y="0px">\n    '
            '<g id="SELECTION">\n        <polygon fill="none" '
            'points="283.055,2.934 283.064,185.447 222.389,185.451 '
            '222.391,224.283 166.576,224.287 166.576,351.707          '
            '92.552,351.711 92.552,49.543 200.954,49.537 200.954,2.963 '
            '282.818,2.963     " style="fill:none"/>\n    </g>\n</svg>',
            apartment.render_outline())

    def test_exceptions(self):
        from ..utilities import cairo_floor_plan_svg
        from ..models import ApartmentError
        apartment = Apartment.fetch_all('test', 1, 1, 1, 3)[7]
        self.assertRaises(ApartmentError,
            cairo_floor_plan_svg, 'no_path', 'no_path', apartment, 'red',
            1, 1, 'red')
        apartment = Apartment.fetch_all('test', 1, 1, 1, 3)[6]
        self.assertRaises(ApartmentError,
            cairo_floor_plan_svg, 'no_path', 'no_path', apartment, 'red',
            1, 1, 'red')

    def test_patterned_id(self):
        apartment1 = Apartment.fetch_all('test', [1], [1], [1], [3])[0]
        apartment8 = Apartment.fetch_all('test', [1], [1], [1], [3])[7]
        pattern = '{b}-{f}-{n}'
        self.assertEqual('1-3-1', apartment1.get_id(pattern))
        self.assertEqual('1-3-8', apartment8.get_id(pattern))
        pattern = '{q}-{s}-{f}-{p}'
        self.assertEqual('1-1-3-1', apartment1.get_id(pattern))
        self.assertEqual('1-1-3-8', apartment8.get_id(pattern))

    def test_in_shorthand(self):
        apartment1 = Apartment.add('test', 1, 1, 1, 1, 1)
        apartment1.building_number = 1
        apartment1.floor_number = 1
        self.assertTrue(apartment1.in_shorthand(['b1-f1_4', 'b7-s4-f29']))
        self.assertFalse(apartment1.in_shorthand(['b1-f2_4', 'b7-s4-f29']))


class UtilityTest(unittest.TestCase):

    def test_parse_shorthand(self):
        from ..utilities import parse_shorthand

        #test canonical form
        shorthand = 'q3-b2-s7-f2_9'
        parsed = parse_shorthand(shorthand)
        self.assertEqual(parsed['quarter_number'], [3])
        self.assertEqual(parsed['building_number'], [2])
        self.assertEqual(parsed['section_number'], [7])
        self.assertEqual(parsed['floor_number'], [2, 3, 4, 5, 6, 7, 8, 9])

        #test incomplete form with alternative range separator
        shorthand = 's3_7-f2_4'
        parsed = parse_shorthand(shorthand)
        assert 'quarters' not in parsed
        self.assertEqual(parsed['section_number'], [3, 4, 5, 6, 7])
        self.assertEqual(parsed['floor_number'], [2, 3, 4])

        #test commas
        shorthand = 's3-f2_6,10_12,14,16_17-p1'
        parsed = parse_shorthand(shorthand)
        self.assertEqual(parsed['section_number'], [3])
        self.assertEqual(parsed['floor_number'], [2, 3, 4, 5, 6, 10, 11, 12, 14, 16, 17])
        self.assertEqual(parsed['pl'], [1])

    def test_close_path(self):
        from art3dutils.utilities import close_path

        #test closed path
        closed_coords = '158.027,320.265 57.99,320.265 57.99,299.073 7.972,299.073 ' \
                 '7.972,238.635 15.948,238.635 15.948,223.536 7.972,223.536 ' \
                 '7.972,90.699 54.864,90.699 54.864,183.19 98.318,183.19 ' \
                 '98.318,199.141 106.446,199.141 106.446,232.045 ' \
                 '158.027,232.045 158.027,320.265'
        closed = close_path(closed_coords)
        self.assertEqual(closed, closed_coords)

        #test open path
        open_coords = '158.027,320.265 57.99,320.265 57.99,299.073 7.972,299.073 '\
                 '7.972,238.635 15.948,238.635 15.948,223.536 7.972,223.536 '\
                 '7.972,90.699 54.864,90.699 54.864,183.19 98.318,183.19 '\
                 '98.318,199.141 106.446,199.141 106.446,232.045 '\
                 '158.027,232.045'
        closed = close_path(open_coords)
        self.assertEqual(closed, closed_coords)

    def test_process_polygon_node(self):
        from art3dutils.utilities import process_node

        polygon_nodes = get_polygon_nodes('svg/polygon_rect_path.svg')
        points_rows = []
        for node in polygon_nodes:
            self.assertEqual(0.0, node.margin_x)
            self.assertEqual(0.0, node.margin_y)
            self.assertEqual(770.0, node.width_)
            self.assertEqual(425.0, node.height_)
            points = process_node(node)
            points_rows.append(points)
        self.assertEqual(
            points_rows[0],
            '283.055,2.934 283.064,185.447 222.389,185.451 222.391,224.283 '
            '166.576,224.287 166.576,351.707 92.552,351.711 92.552,49.543 '
            '200.954,49.537 200.954,2.963 282.818,2.963 283.055,2.934')
        #rect
        self.assertEqual(
            points_rows[2],
            '331.606,229.132 437.192,229.132 437.192,422.078 331.606,422.078 '
            '331.606,229.132')
        #path
        self.assertEqual('386.111,451.387 386.111,460.85 308.896,460.85 '
                         '308.896,330.807 466.497,330.807 466.497,451.387 '
                         '386.111,451.387', points_rows[5])
        #broken path
        self.assertEqual('359.679,148.894 356.887,148.894 356.747,148.894 '
                         '257.555,148.894 257.555,266.026 313.678,266.026 '
                         '313.678,249.552 336.673,249.552 353.878,232.338 '
                         '353.878,229.309 356.957,229.309 356.957,226.516 '
                         '359.679,226.516 404.424,226.516 404.424,148.894 '
                         '359.679,148.894', points_rows[6])

    def test_safe_read_cell(self):
        from art3dutils.utilities import read_cell

        cell = u' 3-х'
        desired_int = read_cell(cell)
        desired_float = read_cell(cell, 'float')
        self.assertEqual(desired_int, 3)
        self.assertEqual(desired_float, 3.0)

        zero = read_cell('')
        self.assertEqual(zero, 0)

        zero = read_cell(u'стр.')
        self.assertEqual(zero, 0)

        square = read_cell(u'789,78', 'float')
        self.assertEqual(square, 789.78)

    def test_mass_replace(self):
        from art3dutils.utilities import mass_replace, DICTIONARY_1S

        with open('xml/1s.xml') as f:
            input = f.read().decode('utf-8')
            xml = mass_replace(input, DICTIONARY_1S)
            dom = parseString(xml.encode('utf-8'))
            output_node = dom.getElementsByTagName('output')
            self.assertEqual(len(output_node), 1)

    def test_progress_bar(self):
        from art3dutils.utilities import progressbar
        items = range(0, 100)
        for num, item in enumerate(progressbar(items)):
            assert item is items[num]

    def test_strip_alpha(self):
        from art3dutils.utilities import strip_alpha

        dirty_string = u'Этаж №6'
        clean_string = strip_alpha(dirty_string)
        self.assertEqual('6', clean_string)

        dirty_string = 'matrix(2 4 5 6 6 7 4)'
        clean_string = strip_alpha(dirty_string, except_=' ')
        self.assertEqual('2 4 5 6 6 7 4', clean_string)