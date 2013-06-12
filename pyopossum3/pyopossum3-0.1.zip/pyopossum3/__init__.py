'''
SQLAlchemy-based access to the oPOSSUM3 TFBS database.
Main file.

Copyright 2013, Konstantin Tretyakov.
http://kt.era.ee/

Licensed under MIT license.


Usage
-----
The primary usage example is the following::

   from pyopossum3 import Opossum
   o = Opossum("mysql://opossum_r:@opossum.cmmt.ubc.ca/oPOSSUM3_human")
   o.ConservedTfbs.query.first().gene.tfbs_counts

The second line creates a connection to the oPOSSUM server, and the third queries the ``conserved_tfbss`` table using SQLAlchemy syntax.

Naturally, for heavy analyses, you are suggested to set up your own copy of the database.
See `here <http://opossum.cisreg.ca/oPOSSUM3/download.html>`_ for instructions on how to download the data.
'''

import os, cPickle

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class Opossum:
    '''
    The main class.
    
    Creating an instance of Opossum establishes the connection to the database,
    collects table metadata, creates ORM classes and sets up the session object::
    
    >> o = Opossum("mysql://opossum_r:@opossum.cmmt.ubc.ca/oPOSSUM3_human")
    
    The resulting instance will have the following useful properties:
    
     * o.ConservedTfbs, o.Gene, o.ExternalGeneId, etc, are objects, mapped to the corresponding oPOSSUM tables.
       you can get the list of all available ORM objects by consulting o.all_orm_classes
     * o.Session is a scoped_session maker. You can use it to query tables as::
        o.Session.query(o.Gene)
     * Alternatively, each ORM class has a "query" property, which does the same as above::
        o.Gene.query
     * Table metadata is available in o.metadata
     * SQLAlchemy engine instance is o.engine
     
    Note that metadata is collected via reflection from the database. After the first query, however, the metadata
    is cached in <cache_dir>/metadata.pickle. You can disable caching by setting cache_dir to None.
    
    Use the ``close`` to complete your session::
    
    >> o.close()
    '''
    
    def __init__(self, url, echo=False, cache_dir=os.path.expanduser("~/.pyopossum3")):
        '''
        Initializes the connection to the database and ORM tables. Parameters:
        
        * url - the URL of the database. The on-line oPOSSUM databases are listed here: http://opossum.cisreg.ca/oPOSSUM3/download.html
          For heavy analyses you should probably obtain a local mirror.
        * echo - when True, SQLAlchemy will echo all SQL statements.
        * cache_dir - the directory where the metadata will be cached (and loaded from). When None, no caching is used and metadata is always
          initialized via reflection.
        '''
        
        # Create engine & init metadata
        self.engine = create_engine(url, echo=echo)
        self.metadata = self._init_metadata(self.engine, cache_dir)
        if self.metadata is None:
            raise Exception("Failed to initialize metadata")
        self._init_orm_tables()
        
    @staticmethod
    def _init_metadata(engine, cache_dir):
        metadata = None
        if cache_dir is not None:
            metadata_pickle = os.path.join(cache_dir, 'metadata.pickle')
            try:
                if os.path.isfile(metadata_pickle):
                    with open(metadata_pickle, 'rb') as f:
                        metadata = cPickle.load(f)
            except: # Failed to load file
                pass
        if metadata is None:  # Try reflection
            metadata = MetaData()
            metadata.reflect(bind=engine)
            if cache_dir is not None:  # Save to cache
                try:
                    if not os.path.isdir(cache_dir):
                        os.mkdir(cache_dir)
                    with open(metadata_pickle, 'wb') as f:
                        cPickle.dump(metadata, f)
                except: # Failed to save for some reason
                    pass
        return metadata

    def _init_orm_tables(self):
        '''
        Initializes all ORM classes.
        I must admit it would have probably been nicer to specify all classes with full attributes in code,
        however just using the reflected metadata seems so much easier.
        '''
        # ORM base class
        Base = declarative_base()
        Session = scoped_session(sessionmaker(bind=self.engine))
        Base.query = Session.query_property()
        Base.q = Base.query
        def to_string(self):
            s = "<%s>\n" % self.__class__.__name__
            for c in self.__table__.columns:
                s += "   |%s: " % c.name + str(getattr(self, c.name)) + "\n"
            return s
        Base.__repr__ = to_string
        
        meta = self.metadata
        # ORM classes. Most properties are reflected from the metadata.
        class Operon(Base):
            __table__ = meta.tables['operons']
        class ConservationLevel(Base):
            __table__ = meta.tables['conservation_levels']
            __mapper_args__ = {'primary_key':meta.tables['conservation_levels'].c.level}
        class TfbsClusterCount(Base):
            __table__ = meta.tables['tfbs_cluster_counts']
            gene = relationship("Gene", backref='tfbs_clusters', primaryjoin="Gene.gene_id == TfbsClusterCount.gene_id", foreign_keys="TfbsClusterCount.gene_id")   
        class Exon(Base):
            __table__ = meta.tables['exons']
            __mapper_args__ = {'primary_key':[meta.tables['exons'].c.gene_id, meta.tables['exons'].c.start]}
            gene = relationship("Gene", backref='exons', primaryjoin="Gene.gene_id == Exon.gene_id", foreign_keys="Exon.gene_id")
        class Promoter(Base):
            __table__ = meta.tables['promoters']
            __mapper_args__ = {'primary_key': meta.tables['promoters'].c.ensembl_transcript_id}
            gene = relationship("Gene", backref='promoters', primaryjoin="Gene.gene_id == Promoter.gene_id", foreign_keys="Promoter.gene_id")
        class ExternalGeneIdType(Base):
            __table__ = meta.tables['external_gene_id_types']
            __mapper_args__ = {'primary_key': meta.tables['external_gene_id_types'].c.id_type}
        class Gene(Base):
            __table__ = meta.tables['genes']
        class DbInfo(Base):
            __table__ = meta.tables['db_info']
            __mapper_args__ = {'primary_key': meta.tables['db_info'].c.build_date}
        class ConservedTfbs(Base):
            __table__ = meta.tables['conserved_tfbss']
            __mapper_args__ = {'primary_key': [meta.tables['conserved_tfbss'].c.gene_id, meta.tables['conserved_tfbss'].c.tf_id, meta.tables['conserved_tfbss'].c.start]}
            gene = relationship("Gene", backref='tfbss', primaryjoin="Gene.gene_id == ConservedTfbs.gene_id", foreign_keys="ConservedTfbs.gene_id")
            @property
            def absolute_start(self):
                return self.gene.start + self.start - 2
            @property
            def absolute_end(self):
                return self.gene.start + self.end - 1
        class ExternalGeneId(Base):
            __table__ = meta.tables['external_gene_ids']
            gene = relationship("Gene", backref='external_ids', primaryjoin="Gene.gene_id == ExternalGeneId.gene_id", foreign_keys="ExternalGeneId.gene_id")
            type = relationship("ExternalGeneIdType", primaryjoin="ExternalGeneIdType.id_type == ExternalGeneId.id_type", foreign_keys="ExternalGeneId.id_type")
        class ConservedRegion(Base):
            __table__ = meta.tables['conserved_regions']
            __mapper_args__ = {'primary_key': [meta.tables['conserved_regions'].c.gene_id, meta.tables['conserved_regions'].c.start]}
            gene = relationship("Gene", backref='conserved_regions', primaryjoin="Gene.gene_id == ConservedRegion.gene_id", foreign_keys="ConservedRegion.gene_id")
        class TfbsCount(Base):
            __table__ = meta.tables['tfbs_counts']
            gene = relationship("Gene", backref='tfbs_counts', primaryjoin="Gene.gene_id == TfbsCount.gene_id", foreign_keys="TfbsCount.gene_id")
            search_region = relationship("SearchRegionLevel", primaryjoin="SearchRegionLevel.level == TfbsCount.search_region_level", foreign_keys="TfbsCount.search_region_level")
            threshold = relationship("ThresholdLevel", primaryjoin="ThresholdLevel.level == TfbsCount.threshold_level", foreign_keys="TfbsCount.threshold_level")
            conservation = relationship("ConservationLevel", primaryjoin="ConservationLevel.level == TfbsCount.conservation_level", foreign_keys="TfbsCount.conservation_level")
        class ThresholdLevel(Base):
            __table__ = meta.tables['threshold_levels']
            __mapper_args__ = {'primary_key': meta.tables['threshold_levels'].c.level}
        class ConservedRegionLength(Base):
            __table__ = meta.tables['conserved_region_lengths']
        class ConservedRegionGenome(Base):
            __table__ = meta.tables['conserved_regions_genome']
            __mapper_args__ = {'primary_key': [meta.tables['conserved_regions_genome'].c.gene_id,meta.tables['conserved_regions_genome'].c.chr,meta.tables['conserved_regions_genome'].c.start] }
        class SearchRegionLevel(Base):
            __table__ = meta.tables['search_region_levels']
            __mapper_args__ = {'primary_key': meta.tables['search_region_levels'].c.level}

        # Create properties of self
        self.all_orm_classes = [
            Operon, 
            ConservationLevel,
            TfbsClusterCount,
            Exon,
            Promoter,
            ExternalGeneIdType,
            Gene,
            DbInfo,
            ConservedTfbs,
            ExternalGeneId,
            ConservedRegion,
            TfbsCount,
            ThresholdLevel,
            ConservedRegionLength,
            ConservedRegionGenome,
            SearchRegionLevel]
        self.Session = Session
        for cls in self.all_orm_classes:
            setattr(self, cls.__name__, cls)
        