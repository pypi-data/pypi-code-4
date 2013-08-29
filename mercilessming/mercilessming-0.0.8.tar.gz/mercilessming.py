"""A minimalistic python dict model for mongodb"""
import sys
import datetime

import bson
import pymongo

##
class Model( dict ):
    """ A dict representation of a MongoDB document """

    # the pymongo database object 
    db = None

    # automatically append creation and modification times on save
    append_times = False

    # a list of default values 
    defaults = {}

    # define if instances of this model should be loaded lazily upon access
    lazy = False

    # a flag that indicates if this model was loaded
    _loaded = False

    #
    def __init__( self, *args, **kwargs ):

        # store the id in the created dict
        args = list( args )
        if 0 < len( args ) and not isinstance( args[ 0 ], dict ):
            args[ 0 ] = { "_id": args[ 0 ] }

        # assign default values
        kwargs = dict( self.defaults, **kwargs )

        super( Model, self ).__init__( dict( *args, **kwargs ) ) # cast to dict for Model cloning
        
    #
    def __repr__( self ):
        return "<%s(%s)>" % ( self.name(), super( Model, self ).__repr__() )

    #
    def __eq__( self, other ):
        if "_id" in self:
            try:
                iter( other )
            except TypeError:
                return False # if other isn't iterable, it can't be equal to Model

            return "_id" in other and self[ "_id" ] == other[ "_id" ]
        return super( Model, self ).__eq__( other )

    #
    def __delitem__( self, key ):
        if key != "_id" and self.lazy and not self._loaded:
            self.load( silent = True )
        return super( Model, self ).__delitem__( key )

    #
    def __setitem__( self, key, value ):
        if key != "_id" and self.lazy and not self._loaded:
            self.load( silent = True )
        return super( Model, self ).__setitem__( key, value )

    #
    def __getitem__( self, key ):
        if key != "_id" and self.lazy and not self._loaded:
            self.load( silent = True )
        return super( Model, self ).__getitem__( key )

    #
    def get( self, key, *args, **kwargs ):
        if key != "_id" and self.lazy and not self._loaded:
            self.load( silent = True )
        return super( Model, self ).get( key, *args, **kwargs )


    # same as dict.update but returns the self instance for easy chaining
    def update( self, *args, **kargs ):
        if self.lazy and not self._loaded:
            self.load( silent = True )
        super( Model, self ).update( *args, **kargs )
        return self

    # 
    def id( self ):
        """ Returns the id of this Model, if exists """
        return self.get( "_id", None )

    #
    def pre_save( self ):
        # add creation and modification time
        if self.append_times:
            self[ "modified_on" ] = datetime.datetime.utcnow()

            if "created_on" not in self:
                self[ "created_on" ] = self[ "modified_on" ]

        # add the id to the document
        id_ = self.id()
        if id_:
            self[ "_id" ] = id_
        elif "_id" in self:
            del self[ "_id" ]

        # encode the data for saving
        data = dict( self ) # copy the data dict of this Model
        data.update( self._encode_data( data ) )

        return data

    #
    def _save( self, data ):
        return self.collection().save( data, safe = True )

    #
    def save( self ):
        data = self.pre_save()
        newid = self._save( data )
        return self.post_save( newid )

    #
    def post_save( self, newid ):
        # update the newly created id
        if self.get( "_id", None ) is None and newid is not None:
            self[ "_id" ] = newid

        return self


    #
    def load( self, silent = False ):
        assert self.get( "_id", None ) is not None, "Unable to load a Model without an id"
        models = self.find( { "_id": self.id() }, limit = 1 )

        if 1 > len( models ):
            if not silent:
                raise KeyError( "Unable to load a a Model with id %s: does not exist" % self[ "_id" ] )
            return self

        self._loaded = True
        self.update( dict( models[ 0 ] ) )
        return self

    #
    def remove( self ):

        assert self.get( "_id", None ) is not None, "Unable to load a Model without an id"
        id_ = self.id()
        assert id_ is not None, "Unable to load a Model without an id"

        self.collection().remove( id_ )
        return self


    #
    @classmethod
    def name( cls ):
        return ".".join( [ cls.__module__, cls.__name__ ] )

    #
    @classmethod
    def connect( cls, db = None ):
        cls.db = db
        return cls

    @classmethod
    def disconnect( cls ):
        # delete instead of resetting to None in order to force the mro to look 
        # up the inheritance tree for the next available db
        delattr( cls, "db" ) 
        return cls

    #
    @classmethod
    def collection( cls ):
        if getattr( cls, "db", None ) is None:
            raise RuntimeError( "%s is not connected to any pymongo database. Use "
                "%s.connect( db ) to fix." % ( cls.__name__, cls.__name__ ) )
        return cls.db[ cls.name() ]

    #
    @classmethod
    def drop( cls ):
        cls.collection().drop()
        return cls

    #
    @classmethod
    def find( cls, *args, **kargs ):
        cursor = cls.collection().find( *args, **kargs )
        models = []
        for entry in cursor:
            entry = cls( entry[ "_id" ], **cls._decode_data( entry ) )
            entry._loaded = True
            models.append( entry )
        return models

    #
    @classmethod
    def find_one( cls, *args, **kargs ):
        return cls.collection().find_one( *args, **kargs )

    #
    @classmethod
    def _encode_data( cls, data, root = True ):
        if isinstance( data, list ):
            data = [ cls._encode_data( el, False ) for el in data ]
        elif isinstance( data, Model ) and root is False:
            classpath = "%s.%s" % ( data.__module__, data.__class__.__name__ )
            data = {
                "__link": { 
                    "classpath": classpath,
                    "id": data.id()
                }
            }
        elif isinstance( data, dict ):
            if "$date" in data:
                return datetime.datetime.utcfromtimestamp( int( data[ "$date" ] ) / 1000 )
            
            for name, value in data.items():
                data[ name ] = cls._encode_data( value, False )

        return data

    #
    @classmethod
    def _decode_data( cls, data ):
        if isinstance( data, list ):
            data = [ cls._decode_data( el ) for el in data ]
        elif isinstance( data, dict ) and "__link" in data:
            classpath = data[ "__link" ][ "classpath" ]
            id_ = data[ "__link" ][ "id" ]
            classpath = classpath.split( "." )
            class_ = classpath[ -1 ]
            module = ".".join( classpath[ :-1 ] ) or "__main__"

            if module not in sys.modules:
                raise NameError( "module '%s' is not defined" % module )
            module = sys.modules[ module ]

            if not hasattr( module, class_ ):
                raise AttributeError( "'module' object has no attribute '%s'" % class_ )
            ModelClass = getattr( module, class_ )
            data = ModelClass( id_ )
        elif isinstance( data, dict ):
            for name, value in data.items():
                data[ name ] = cls._decode_data( value )
        return data

    #
    @classmethod
    def save_batch( cls, models ):

        # validate all models belong to this class to avoid a situation 
        # where models aren't saved to the correct collection
        for model in models:
            assert model.__class__ == cls, "Can't batch insert of different" + \
                "types. Expected: %s, received: %s" % ( cls.__name__, model.__class__.__name__ )

        # pre-save all models
        docs = []
        for model in models:
            docs.append( model.pre_save() )

        # batch insert, or fall back to sequential updates
        newids = []
        try:
            newids = cls.collection().insert( docs, safe = True )
        except pymongo.errors.DuplicateKeyError:
            # mongo doesn't provide a batch-update command,
            # we'll just fallback to sequential updates
            for doc in docs:
                newid = model._save( doc )
                newids.append( newid )

        # post-save all models
        for model, id_ in zip( models, newids ):
            model.post_save( id_ )

        return models