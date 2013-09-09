# -*- coding: utf-8 -*-

import re
import os
import locale
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.sql import and_
from sqlalchemy import (Column, Table, Integer, ForeignKey, Unicode, Float,
                        MetaData, Boolean, VARCHAR)
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from xml.dom.minidom import parseString, parse
from collections import Mapping

#TODO rewrite this to simple import
from .utilities import (
    get_polygon_nodes, process_node, get_outline_container,
    get_text_nodes, get_svg_viewbox,
    get_text_coords, remove_child_nodes,
    area_coords, node2svg, prepare_outline_svg,
    write_scaled_svg, parse_shorthand, to_list
)

ATTR_TYPES = {
    'quarter_number': ('q', 'int'),
    'building_number': ('b', 'int'),
    'section_number': ('s', 'int'),
    'floor_number': ('f', 'int'),
    'number': ('n', 'int'),
    'room_count': ('rc', 'int'),
    'square': ('sq', 'float'),
    'status': ('st', 'int'),
    'total_cost': ('tc', 'int'),
    'cost_per_meter': ('cpm', 'int'),
    'type': ('t', 'unicode'),
    'note': ('nt', 'unicode')
}

session = None
metadata = MetaData()
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def populate_session(db_path=None, create_tables=False, outer_session=None):

    global session

    if db_path and not outer_session:
        engine = create_engine(db_path)
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        if create_tables:
            metadata.create_all(engine)
    else:
        session = outer_session

    return session


class ApartmentError(Exception):
    """General apartment exception"""
    def __init__(self, apartment, message_point='Error'):
        message = '%s for q%d-b%d-s%d-f%d-p%d' %\
                  (message_point, apartment.quarter_number,
                   apartment.building_number, apartment.section_number,
                   apartment.floor_number, apartment.pl)

        Exception.__init__(self, message)
        self.apartment = apartment


class FloorError(Exception):

    def __init__(self, floor):
        message = 'No svg path for floor: q%d-b%d-s%d-f%d' % \
                  (floor.quarter_number, floor.building_number,
                   floor.section_number, floor.number)

        Exception.__init__(self, message)
        self.floor = floor


class Entity(object):

    @property
    def fs_name(self):
        """Return class name for use in filesystem (directories, etc.)"""
        return self.__class__.__name__.lower()

    @classmethod
    def fetch(cls, key):
        return session.query(cls).get(key)

    @classmethod
    def fetch_all(cls, project_title=None, shorthand=None, limit=None,
                  sort_keys=('quarter_number', 'building_number',
                             'section_number', 'floor_number', 'number'),
                  **filters):
        """
        Fetch all entities. Filter by project_title, shorthand or
        arbitrary `filters`, sort by `sort_keys`.
        """
        if shorthand:
            value_dict = parse_shorthand(shorthand)
        else:
            value_dict = filters

        order_criteria = [getattr(cls, key, None) for key in sort_keys]
        query = session.query(cls).order_by(*order_criteria)

        if project_title:
            query = query.filter(cls.project_title == project_title)

        for attrib_name, value in value_dict.items():
            column = getattr(cls, attrib_name)
            query = query.filter(column.in_(to_list(value)))

        if limit:
            query = query.limit(limit)
        return query.all()


class Project(Entity):

    def __init__(self, title, quarters=None):
        self.title = title
        self.quarters = quarters or []

    def fetch_apartments(self, available_only=False):
        query = session.query(Apartment)\
                       .filter(apartments.c.project_title == self.title)
        if available_only:
            query = query.filter(apartments.c.status == 1)
        return query.all()


class Quarter(Entity):

    def __init__(self, number=0, buildings=None):
        self.number = number
        self.buildings = buildings or []

    def fetch_available_buildings(self):
        available = []
        for building in self.buildings:
            if len(building.fetch_apartments(True)) > 0:
                available.append(building)
        return available


class Building(Entity, Mapping):

    def __init__(self, number=0, sections=None):
        self.number = number
        self.sections = sections or []

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def fetch_floors(self, floor_numbers=None):
        query = session.query(Floor).filter(floors.c.building_number==self.number)
        if floor_numbers:
            query = query.filter(floors.c.number.in_(list(floor_numbers)))
        return query.all()

    def fetch_apartments(self, available_only=False, floors=None):
        query = session.query(Apartment)\
                       .filter(apartments.c.project_title==self.project_title,
                               apartments.c.quarter_number==self.quarter_number,
                               apartments.c.building_number==self.number)
        if floors:
            floor_list = list(floors)
            query = query.filter(apartments.c.floor_number.in_(floor_list))
        if available_only:
            query = query.filter(apartments.c.status == 1)
        return query.all()

    def get_sections(self, reverse=False):
        """Get sections sorted"""
        sections = self.sections
        result = sorted(sections, key=lambda sec: sec.number, reverse=reverse)
        return result


class Section(Entity, Mapping):

    def __init__(self, number=0, floors=None):
        self.number = number
        self.floors = floors or []

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def fetch_apartments(self, available_only=False, room_count=None):
        query = session.query(Apartment)\
                       .filter(apartments.c.project_title==self.project_title,
                               apartments.c.quarter_number==self.quarter_number,
                               apartments.c.building_number==self.building_number,
                               apartments.c.section_number==self.number)
        if available_only:
            query = query.filter(apartments.c.status == 1)
        if room_count:
            query = query.filter(apartments.c.room_count == room_count)
        return query.all()

    def fetch_floors(self, available_only=False):
        all_floors = session.query(Floor)\
                       .filter(apartments.c.project_title==self.project_title,
                               floors.c.quarter_number==self.quarter_number,
                               floors.c.building_number==self.building_number,
                               floors.c.section_number==self.number)
        if available_only:
            available_floors = []
            for floor in all_floors:
                if len(floor.fetch_apartments(available_only=True)):
                    available_floors.append(floor)
            return available_floors
        else:
            return all_floors

    def pick_file(self, directory, path=True):
        """Find an appropriate file in a directory"""

        picked_file = self.floors[0].apartments[0].pick_file(directory, path)
        return picked_file

    def area_coords(self, buildings_dir, size=None, reverse=False,
                    padding=(0, 0, 0, 0)):
        """Return polygon coordinates in html area tag format removing margin"""
        #TODO extract this into separate function
        outline_node = None
        reverse = not reverse
        svg_path = self.pick_file(buildings_dir)
        if size:
            dom_ = parse(svg_path)
            prepare_outline_svg(dom_)
            filename = '__outlines__.svg'
            write_scaled_svg(dom_, size=size, filename=filename,
                             padding=padding)
            nodes = get_polygon_nodes(filename)
        else:
            nodes = get_polygon_nodes(svg_path)
        if not len(nodes):
            raise ApartmentError(self, 'Bad outlines in %s' % svg_path)
        sections = self.building.get_sections(reverse=reverse)
        for (section, node) in zip(sections, nodes):
            if section is self:
                outline_node = node

        if not outline_node:
            raise ApartmentError(self, message_point='No outline in %s' %
                                                     svg_path)
        return area_coords(outline_node)


class Floor(Entity, Mapping):

    def __init__(self, number=0, apartments=None, svg_path=None):
        self.number = number
        self.apartments = apartments or []
        self.svg_path = svg_path

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def get_apartments(self, available_only=False, reverse=False,
                       room_count=None):
        """Get floor apartments filtered or sorted"""
        apts = self.apartments
        if available_only:
            apts = filter(lambda apt: apt.status is 1, apts)
        if room_count is not None:
            apts = filter(lambda apt: apt.room_count is room_count, apts)
        result = sorted(apts, key=lambda apt: apt.number, reverse=reverse)
        return result

    def fetch_apartments(self, available_only=False, reverse=False,
                         room_count=None):
        """Mock fetch_apartments as uniform method"""
        return self.get_apartments(available_only, reverse, room_count)

    def pick_file(self, dir_):
        """Return appropriate file path"""
        return self.apartments[0].pick_file(dir_)

    def get_square_extremum(self, extremum='max'):
        """Return max or min value of apartment squares on the floor"""
        result = None
        square_list = [apt.square for apt in self.get_apartments()]
        if extremum is 'max':
            result = max(square_list)
        if extremum is 'min':
            result = min(square_list)
        return result


class Apartment(Entity, Mapping):

    def __init__(self, number,
                 room_count=None, square=0, total_cost=0, cost_per_meter=0,
                 status=True, square_out=None, note=None, type_=None,
                 open_=True):
        self.number = number
        self.room_count = room_count
        self.square = square
        self.square_out = square_out
        self.total_cost = total_cost
        self.cost_per_meter = cost_per_meter
        self.status = status
        self.open = open_
        self.note = note
        self.type = type_

    def __len__(self):
        return len(self.get_full_dict())

    def __iter__(self):
        for key, value in self.get_full_dict().items():
            yield key

    def __getitem__(self, key):
        return self.get_full_dict().get(key)

    @property
    def shorthand(self):
        """Return shorthanded id of the apartment"""
        return ('q{quarter_number}-b{building_number}-'
                's{section_number}-f{floor_number}-n{number}'
                ).format(
                    quarter_number=self.quarter_number,
                    building_number=self.building_number,
                    section_number=self.section_number,
                    floor_number=self.floor_number,
                    number=self.number
                )

    @classmethod
    def add(cls, project_title, number, quarter_number=0, building_number=0,
            section_number=0, floor_number=0, square=None,
            room_count=None, square_out=None, status=None,
            cost_per_meter=None, total_cost=None, note=None):
        project = Project.fetch(project_title) or Project(project_title)
        quarter = Quarter.fetch((project_title, quarter_number)) or \
            Quarter(quarter_number)
        building = Building.fetch((project_title,
                                   quarter_number,
                                   building_number)) or \
            Building(building_number)
        section = Section.fetch((project_title,
                                 quarter_number,
                                 building_number,
                                 section_number)) or Section(section_number)
        floor = Floor.fetch((project_title,
                             quarter_number,
                             building_number,
                             section_number,
                             floor_number)) or Floor(floor_number)
        apartment = Apartment.fetch((project_title,
                                     quarter_number,
                                     building_number,
                                     section_number,
                                     floor_number,
                                     number)) or Apartment(number)
        project.quarters.append(quarter)
        quarter.buildings.append(building)
        building.sections.append(section)
        section.floors.append(floor)
        floor.apartments.append(apartment)
        session.add(project)
        apartment.building_number = building_number
        apartment.floor_number = floor_number
        apartment.number = number
        apartment.room_count = room_count
        apartment.square = square
        apartment.square_out = square_out
        apartment.status = status
        apartment.cost_per_meter = cost_per_meter
        apartment.total_cost = total_cost
        apartment.note = note
        return apartment

    def area_coords(self, floor_dir=None, size=None, reverse=False,
                    padding=(0, 0, 0, 0), skip_count_check=False,
                    siblings=None):
        """
        Return polygon coordinates in html area tag format removing margin
        """
        #TODO extract this into separate function
        outline_node = svg_path = None
        reverse = not reverse
        if floor_dir:
            orig_svg_path = self.pick_file(floor_dir)
            if size:
                dom_ = parse(orig_svg_path)
                try:
                    prepare_outline_svg(dom_)
                except IndexError:
                    raise ApartmentError(self, 'Failed prepare outline svg')
                svg_path = '__outlines__.svg'

                write_scaled_svg(dom_, size=size, filename=svg_path,
                                 padding=padding)

                nodes = get_polygon_nodes(svg_path, skip_id_check=True,
                                          skip_count_check=skip_count_check)
            else:
                nodes = get_polygon_nodes(svg_path)
            if not nodes:
                raise ApartmentError(self, 'No nodes in %s' % svg_path)
            apartments = []
            if siblings:
                apartments = siblings
            else:
                apartments = self.floor.get_apartments(reverse=reverse)
            for (apartment, node) in zip(apartments, nodes):
                if apartment is self:
                    outline_node = node
        else:
            outline_node = self._get_node()
        if not outline_node:
            raise ApartmentError(self,
                                 message_point='No outline in %s '
                                               '(out of total %d outlines)' %
                                               (orig_svg_path, len(nodes)))
        return area_coords(outline_node)

    def get_outline_id(self, floor_dir, complex=False):
        """Return id found in outlines id attribute in svg"""
        outline_node = None
        svg_path = self.pick_file(floor_dir)
        nodes = get_polygon_nodes(svg_path)
        apartments = self.floor.fetch_apartments(reverse=True)
        for (apartment, node) in zip(apartments, nodes):
            if apartment is self:
                outline_node = node
        if not outline_node:
            raise ApartmentError(self, message_point='No outline')
        if complex:
            dirty_id = str(outline_node.getAttribute('id').replace('_x3', ''))
            parts = dirty_id.split('_')
            part1 = parts[0]
            part2 = parts[1][0]
            part3 = parts[1][1]
            literal = ''
            if len(parts[1]) is 3:
                literal = parts[1][2]
            return '%s-%s.%s%s' % (part1, part2,  part3, literal)
        else:
            return str(outline_node.getAttribute('id'))

    @staticmethod
    def get_center(node):
        """
        Get the center of polygon's outer rectangle
        """
        coords = process_node(node)
        try:
            pairs = re.split(' ', coords)
            x_coords = [float(re.split(',', pair)[0]) for pair in pairs]
            y_coords = [float(re.split(',', pair)[1]) for pair in pairs]
            point1 = (min(x_coords), max(y_coords))
            point2 = (max(x_coords), min(y_coords))
            width = point2[0]-point1[0]
            height = point1[1]-point2[1]
            return point1[0]+width/2.0, point2[1]+height/2.0
        except TypeError:
            return None

    @property
    def pl(self):
        """Get `number on floor` for the apartment"""
        apartments = self.floor.get_apartments()
        for num, apt in enumerate(apartments):
            if apt is self:
                return num + 1

    def localize_square(self, symbol=True):
        u"""Return square in russian locale (with `м²`)"""
        result = None
        if self.square:
            result = locale.format('%g', self.square)
            if symbol:
                sq = u'²'
                if getattr(self, 'no_sq_symbol', False):
                    sq = u'<sup>2</sup>'
                result = u'{square_str} м{sq}'.format(square_str=result, sq=sq)
        return result

    def total_cost_localized(self, calculated=False, symbol=True):
        u"""Return total cost in russian locale"""
        total_cost = self.total_cost
        if calculated:
            if self.calc_total_cost():
                total_cost = self.calc_total_cost()
            else:
                total_cost = 0
        cost_str = locale.format('%d', total_cost, True, symbol)
        result = cost_str
        return result

    def no_square_symbol(self):
        """
        Set special flag to indicate `square_localized` that there is no '²'
        symbol in the font
        """
        self.no_sq_symbol = True

    def get_full_dict(self):
        """Get apt's properties as `dict` including dynamic properties"""
        base_dict = self.__dict__
        base_dict['pl'] = self.pl
        base_dict['square_localized'] = self.localize_square()
        return base_dict

    def render_outline(self, source_dir, node_name=None, bound_box=False,
                       reverse=False, find_by_shorthand=False, attribs=None,
                       style_attribs=True, skip_count_check=False,
                       siblings=None):
        """Render apartment outline svg file with style attributes"""

        svg_ = None
        svg_path = self.pick_file(source_dir)
        poly_nodes = get_polygon_nodes(svg_path,
                                       skip_count_check=skip_count_check)
        if not poly_nodes:
            raise ApartmentError(self,
                                 'Bad outlines in {0}'.format(svg_path))

        if not find_by_shorthand:
            if siblings:
                apartments = siblings
            else:
                apartments = self.floor.get_apartments(reverse=not reverse)
            for (apartment, node) in zip(apartments, poly_nodes):
                if apartment is self:
                    svg_ = node2svg(node)
        else:
            for node in poly_nodes:
                shorthand_str = node.getAttribute('id')
                if self.in_shorthand(shorthand_str):
                    svg_ = node2svg(node)
        if svg_:
            dom_ = parseString(svg_)
        else:
            raise ApartmentError(self,
                                 'No outline in '
                                 '{path}'.format(path=svg_path))
        node = get_polygon_nodes(dom_=dom_,
                                 skip_count_check=skip_count_check)[0]

        if node_name:
            points = node.getAttribute('points')
            selection_node = get_outline_container(dom_)
            selection_node.removeChild(node)
            node = dom_.createElement(node_name)
            node.setAttribute('points', points)
            selection_node.appendChild(node)

        if bound_box:
            svg_node = dom_.getElementsByTagName('svg')[0]
            view_box = get_svg_viewbox(dom_)
            box = dom_.createElement('rect')
            box.setAttribute('x', str(view_box['margin_x']))
            box.setAttribute('y', str(view_box['margin_y']))
            box.setAttribute('width', str(view_box['width']))
            box.setAttribute('height', str(view_box['height']))
            box.setAttribute('style', 'fill:none; stroke:red; stroke-width:4')
            svg_node.appendChild(box)

        if style_attribs:
            style = []
            for name, value in attribs.items():
                style.append('{name}:{value}'.format(name=name, value=value))
            if 'fill' not in attribs:
                style.append('fill:none')
            if len(style):
                node.setAttribute('style', ';'.join(style))
        else:
            for name, value in attribs.items():
                node.setAttribute(name, str(value))

        return dom_.toxml()

    def render_floor(self, path, text_fill=None):
        """Render floor xml data optionally with additions like apt numbers"""

        floor_dom = parse(self.pick_file(path, True))

        if text_fill:
            apartments = self.floor.fetch_apartments(reverse=True)
            for (apartment, text_node) in zip(apartments,
                                              get_text_nodes(dom_=floor_dom)):
                remove_child_nodes(text_node)
                text_node.setAttribute('style', 'fill:%s' % text_fill)
                text_node.setAttribute('font-size', '10')
                text_node.setAttribute('font-family', 'DejaVu Serif')
                x, y = get_text_coords(text_node)
                text_node.setAttribute('x', str(x - 10))
                text_node.setAttribute('y', str(y + 0.5))
                text_node.removeAttribute('transform')
                text = floor_dom.createTextNode(u'кв.%s' % apartment.number)
                text_node.appendChild(text)

        return floor_dom.toxml(encoding='utf-8')

    def pick_file(self, directory, path=True, **additional):
        """
        Find an appropriate file in a directory and return its name or path.
        """
        for filename in os.listdir(directory):
            basename = os.path.basename(filename)
            clean_name = os.path.splitext(basename)[0]
            try:
                if self.in_shorthand(clean_name, **additional):
                    if path:
                        return os.path.join(directory, filename)
                    else:
                        return filename
            except AttributeError as error:
                raise ApartmentError(self, error.message)
        raise ApartmentError(self, 'No file in %s' % directory)

    def in_shorthand(self, shorthand_list, **additional):
        """Return `True` if the apartment fits in any of shorthand strings """
        shorthand_list = to_list(shorthand_list)
        record_checks = []
        for name, value in additional.items():
            setattr(self, name, value)
        for shorthand in shorthand_list:
            checks = []
            parsed_data = parse_shorthand(shorthand)
            for name, range_ in parsed_data.iteritems():
                try:
                    attr_val = getattr(self, name, False)
                except AttributeError:
                    raise AttributeError('Attribute `{attr_name}`'
                                         ' not provided'.format(
                                         attr_name=name))
                checks.append(attr_val in range_)
            record_checks.append(all(checks))
        return any(record_checks)

    def get_id(self, pattern):
        """
        Return apartment id according to given pattern
        """
        return pattern.format(**self)

    def calc_total_cost(self, format=False):
        """Calculate total cost"""
        result = None
        if self.cost_per_meter and self.square:
            result = int(float(self.square) * int(self.cost_per_meter))
        return result

    def calc_room_count(self):
        """
        Calculate room count by square. Based on a table, received from
        'Life-Mitinskaya' project
        """
        SQUARE_MAP = {
            0: (None, 30),
            1: (35, 50),
            2: (51, 70),
            3: (75, 90),
            4: (91, 100),
            5: (110, None)
        }

        result = None
        if self.square:
            for rc, range_ in SQUARE_MAP.items():
                min_, max_ = range_
                min_check = True
                max_check = True
                if min_:
                    min_check = self.square >= min_
                if max_:
                    max_check = self.square <= max_
                if all([min_check, max_check]):
                    result = rc
                    break
        return result

    def get_actual_status(self, expired, reserved_status=3):
        """Check expiry and return the correct status"""
        status = int(self.status)
        if status is reserved_status:
            if self.shorthand in expired:
                status = self.status = 1
                session.merge(self)
        return status


projects = Table('project', metadata,
                 Column('title', VARCHAR(255), primary_key=True,
                        nullable=False),
                 mysql_engine='MyISAM', mysql_charset='utf8')

quarters = Table('quarter', metadata,
                 Column('project_title', VARCHAR(255),
                        ForeignKey('project.title'),
                        primary_key=True),
                 Column('number', Integer, primary_key=True, nullable=False,
                        autoincrement=False),
                 mysql_engine='MyISAM', mysql_charset='utf8')

buildings = Table('building', metadata,
                  Column('project_title', VARCHAR(255),
                         ForeignKey('quarter.project_title'),
                         primary_key=True),
                  Column('quarter_number', Integer,
                         ForeignKey('quarter.number'),
                         primary_key=True),
                  Column('number', Integer, primary_key=True, nullable=False,
                         autoincrement=False), mysql_engine='MyISAM',
                  mysql_charset='utf8')

sections = Table('section', metadata,
                 Column('project_title', VARCHAR(255),
                        ForeignKey('building.project_title'),
                        primary_key=True),
                 Column('quarter_number', Integer,
                        ForeignKey('building.quarter_number'),
                        primary_key=True),
                 Column('building_number', Integer,
                        ForeignKey('building.number'),
                        primary_key=True),
                 Column('number', Integer, primary_key=True, nullable=False,
                        autoincrement=False), mysql_engine='MyISAM',
                 mysql_charset='utf8')

floors = Table('floor', metadata,
               Column('project_title', VARCHAR(255),
                      ForeignKey('section.project_title'),
                      primary_key=True),
               Column('quarter_number', Integer,
                      ForeignKey('section.quarter_number'),
                      primary_key=True),
               Column('building_number', Integer,
                      ForeignKey('section.building_number'),
                      primary_key=True),
               Column('section_number', Integer, ForeignKey('section.number'),
                      primary_key=True),
               Column('number', Integer, primary_key=True, nullable=False,
                      autoincrement=False),
               mysql_engine='MyISAM', mysql_charset='utf8')

apartments = Table('apartment', metadata,
                   Column('project_title', VARCHAR(255),
                          ForeignKey('floor.project_title'),
                          primary_key=True),
                   Column('quarter_number', Integer,
                          ForeignKey('floor.quarter_number'),
                          primary_key=True),
                   Column('building_number', Integer,
                          ForeignKey('floor.building_number'),
                          primary_key=True),
                   Column('section_number', Integer,
                          ForeignKey('floor.section_number'),
                          primary_key=True),
                   Column('floor_number', Integer, ForeignKey('floor.number'),
                          primary_key=True),
                   Column('number', Integer, primary_key=True, nullable=False,
                          autoincrement=False),
                   Column('room_count', Integer),
                   Column('square', Float),
                   Column('square_out', Float),
                   Column('total_cost', Integer),
                   Column('cost_per_meter', Integer),
                   Column('status', Integer),
                   Column('open', Boolean),
                   Column('note', VARCHAR(255)),
                   Column('type', VARCHAR(255)),
                   mysql_engine='MyISAM',
                   mysql_charset='utf8')

mapper(Project, projects, properties={
    'quarters': relationship(Quarter, backref='project',
                             cascade="all, delete-orphan")
})
mapper(Quarter, quarters, properties={
    'buildings': relationship(Building, backref='quarter',
                              primaryjoin=and_(
                                  buildings.c.quarter_number ==
                                  quarters.c.number,
                                  buildings.c.project_title ==
                                  quarters.c.project_title
                              ),
                              cascade="all, delete-orphan")
})
mapper(Building, buildings, properties={
    'sections': relationship(Section, backref='building',
                             primaryjoin=and_(
                                 sections.c.building_number ==
                                 buildings.c.number,
                                 sections.c.quarter_number ==
                                 buildings.c.quarter_number,
                                 sections.c.project_title ==
                                 buildings.c.project_title
                             ),
                             cascade="all, delete-orphan")
})
mapper(Section, sections, properties={
    'floors': relationship(Floor, backref='section',
                           primaryjoin=and_(
                               floors.c.section_number == sections.c.number,
                               floors.c.building_number ==
                               sections.c.building_number,
                               floors.c.quarter_number ==
                               sections.c.quarter_number,
                               floors.c.project_title ==
                               sections.c.project_title
                           ),
                           cascade="all, delete-orphan")
})
mapper(Floor, floors, properties={
    'apartments': relationship(Apartment, backref='floor',
                               primaryjoin=and_(
                                   apartments.c.floor_number ==
                                   floors.c.number,
                                   apartments.c.section_number ==
                                   floors.c.section_number,
                                   apartments.c.building_number ==
                                   floors.c.building_number,
                                   apartments.c.quarter_number ==
                                   floors.c.quarter_number,
                                   apartments.c.project_title ==
                                   floors.c.project_title
                               ),
                               cascade="all, delete-orphan")
})
mapper(Apartment, apartments)