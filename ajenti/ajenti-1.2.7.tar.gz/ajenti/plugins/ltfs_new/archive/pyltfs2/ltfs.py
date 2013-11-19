from lxml import etree

import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relation


Base = declarative_base()


class Tape (Base):
    __tablename__ = 'tapes'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    uuid = Column(String(255))
    generation = Column(Integer)
    custom_a = Column(String(255))
    custom_b = Column(String(255))
    custom_c = Column(String(255))
    custom_d = Column(String(255))


class Entry (Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String(255))
    is_dir = Column(Boolean)
    read_only = Column(Boolean)
    length = Column(BigInteger)
    parent_id = Column(Integer, ForeignKey('entries.id', ondelete='CASCADE'), nullable=True)
    parent = relation('Entry', remote_side=[id])
    tape_id = Column(Integer, ForeignKey('tapes.id', ondelete='CASCADE'), nullable=True)
    tape = relation('Tape', uselist=False)

    def path(self):
        e = self
        r = ''
        while e:
            r = '/' + e.name + r
            e = e.parent
        return r


class LTFS (object):
    def __init__(self, url, debug=False):
        self.engine = sqlalchemy.create_engine(url, echo=debug, convert_unicode=True, encoding='utf-8')
        try:
            Base.metadata.create_all(self.engine)
        except:
            pass
        self.session = sessionmaker(bind=self.engine)()

    def delete_tape(self, name=None):
        tapes = []
        if name:
            tapes += self.session.query(Tape).filter(Tape.name == name).all()
        for tape in tapes:
            self.session.delete(tape)
        self.session.commit()

    def get_tape(self, name=None):
        tapes = []
        if name:
            tapes += self.session.query(Tape).filter(Tape.name == name).all()
        return tapes[0] if tapes else None

    def create_tape(self, xml, name, custom_a='', custom_b='', custom_c='', custom_d=''):
        xml = etree.fromstring(xml)

        tape = Tape(
            name=name,
            custom_a=custom_a,
            custom_b=custom_b,
            custom_c=custom_c,
            custom_d=custom_d,
            uuid=xml.find('volumeuuid').text,
            generation=xml.find('generationnumber').text,
        )

        self.session.add(tape)

        def recurse(cwd, element):
            print '%i entries parsed' % recurse.counter
            for eroot in ([element] + [element.find('contents')]):
                if not eroot:
                    continue
                for edir in eroot.getchildren():
                    if edir.tag == 'directory':
                        recurse.counter += 1
                        dir = Entry(
                            parent=cwd,
                            uid=edir.find('fileuid').text,
                            name=edir.find('name').text,
                            read_only=edir.find('readonly').text == 'true',
                            is_dir=True,
                            tape=tape,
                        )
                        self.session.add(dir)
                        recurse(dir, edir)
                for efile in eroot.getchildren():
                    if efile.tag == 'file':
                        recurse.counter += 1
                        file = Entry(
                            parent=cwd,
                            uid=efile.find('fileuid').text,
                            name=efile.find('name').text,
                            read_only=efile.find('readonly').text == 'true',
                            length=int(efile.find('length').text),
                            is_dir=False,
                            tape=tape,
                        )
                        self.session.add(file)

                        if recurse.counter % 100 == 0:
                            self.session.commit()

        recurse.counter = 0
        recurse(None, xml)
        self.session.commit()

    def ls(self, tape, cwd):
        files = self.session.query(Entry).filter(sqlalchemy.and_(Entry.parent == cwd, Entry.tape == tape)).all()
        print len(files), tape, cwd
        
        def _cmp(a, b):
            if a.is_dir == b.is_dir:
                return cmp(a.name, b.name)
            elif b.is_dir:
                return 1
            return -1

        files = sorted(files, cmp=_cmp)
        return files

    def search(self, query, search_files=True, limit=10000, offset=0):
        class SearchResult (object):
            pass

        class FoundNode (object):
            pass

        searchResult = SearchResult()
        searchResult.tapes = []
        searchResult.nodes = []

        found_tapes = self.session.query(Tape) \
            .filter(sqlalchemy.or_(
                Tape.name.ilike('%' + query + '%'),
                Tape.custom_a.ilike('%' + query + '%'),
                Tape.custom_b.ilike('%' + query + '%'),
                Tape.custom_c.ilike('%' + query + '%'),
                Tape.custom_d.ilike('%' + query + '%')
            )) \
            .all()

        searchResult.tapes += list(found_tapes)

        if search_files:
            found_files = self.session.query(Entry).filter(Entry.name.ilike('%' + query + '%')).all()
            searchResult.nodes += list(found_files)

        searchResult.total = len(searchResult.nodes)
        searchResult.nodes = searchResult.nodes[offset:offset+limit]
        return searchResult
