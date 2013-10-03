import base64
import pickle
from collections import defaultdict
from mock import Mock

from tahoe.models import ModelRegistry

from tahoe.models.mixins.encodable import EncoderMixin
from tahoe.models.mixins.searchable import SearchableMixin
from tahoe.models.mixins.timestampable import TimestampMixin

from tahoe import search

from tahoe.tests import TahoeTestCase


class TestEncoderMixin(TahoeTestCase):
    def test_encoder_mixin(self):
        """
        EncoderMixin: Test encoder and decoder chains
        """
        class TestBase(EncoderMixin):
            encode_decode_chain = [
                (pickle.dumps, pickle.loads),
                (base64.b64encode, base64.b64decode)]

        tb = TestBase()

        data = dict(
            one="one",
            two="two",
            three="three")

        encoded_data = tb.encode(data)
        assert encoded_data
        decoded_data = tb.decode(encoded_data)
        assert decoded_data

        assert decoded_data == data
        assert encoded_data != data

    def test_encoder_mixin_fails_with_bad_chain(self):
        """
        EncoderMixin: Decoding and Encoding fail with bad settings
        """
        class TestBadChain(EncoderMixin):
            encode_decode_chain = [
                (base64.b64encode, pickle.loads),
                (pickle.dumps, base64.b64decode)]

        tb = TestBadChain()

        data = dict(
            one="one",
            two="two",
            three="three")

        with self.assertRaises(Exception):
            tb.encode(data)


class TestTimestampMixin(TahoeTestCase):
    @staticmethod
    def make_callback():
        def callback(*callback_args, **callback_kwargs):
            db = callback_kwargs.get('db')

            class TestModel(db.Model,
                            TimestampMixin(callback_kwargs.get('db'))):
                pass
            return TestModel
        return callback

    def setUp(self):
        self.mock_config = Mock(name='config')
        self.mock_app = Mock(name='app')
        self.mock_logger = Mock(name='logger')
        self.mock_bucket = defaultdict(Mock)
        self.mock_query = Mock(name='query')
        self.mock_filter = Mock(name='filter')

        self.mock_query.filter = self.mock_filter

        class ModelClass(object):
            query = self.mock_query

        self.mock_db = Mock(name='db')
        self.mock_db.Model = ModelClass

        ModelRegistry.destroy_all()

    def test_timestamp_mixin(self):
        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert 'TestModel' in mr.models
        assert mr.TestModel

        assert self.mock_db.Column.call_count == 3

        # Verify inhereted class attributes
        assert hasattr(mr.TestModel, 'NOW_FN')
        assert hasattr(mr.TestModel, 'created_at')
        assert hasattr(mr.TestModel, 'updated_at')
        assert hasattr(mr.TestModel, 'deleted_at')
        assert hasattr(mr.TestModel, 'query_active')
        assert hasattr(mr.TestModel, 'query')

        q = mr.TestModel.query_active()

        assert q
        assert self.mock_filter.called_with(False)

        # Instance attributes
        tm = mr.TestModel()
        assert hasattr(tm, 'is_deleted')
        assert hasattr(tm, 'mark_deleted')
        assert hasattr(tm, 'mark_undeleted')

        tm.mark_undeleted()
        assert not tm.is_deleted()
        tm.mark_deleted()
        assert tm.is_deleted()


class TestSearchableMixin(TahoeTestCase):
    @staticmethod
    def make_callback(bad=False):
        def callback(*callback_args, **callback_kwargs):
            bucket = callback_kwargs.get('bucket')
            logger = callback_kwargs.get('logger')
            db = callback_kwargs.get('db')

            class TestModel(db.Model,
                            SearchableMixin(bucket=bucket, logger=logger)):
                @classmethod
                def _search_index_mapping(cls):
                    return dict(properties=dict(
                        id=search.EXACT_MATCH_FIELD.to_dict(),
                        email=search.CASE_INSENSITIVE_EXACT.to_dict(),
                        username=search.CASE_INSENSITIVE_EXACT.to_dict()))

                @classmethod
                def _search_builder_mapping(self):
                    return dict(
                        id=search.ExactMatch('id'),
                        email=search.CaseInsensitiveExact('email'),
                        username=search.CaseInsensitivePrefix('username'),
                        username_exact=search.CaseInsensitiveExact('username'),
                        q=search.StringQuery())

            class TestModelBad(db.Model,
                               SearchableMixin(bucket=bucket, logger=logger)):
                pass

            if bad:
                return TestModelBad
            return TestModel
        return callback

    def setUp(self):
        self.mock_config = Mock(name='config')
        self.mock_app = Mock(name='app')
        self.mock_logger = Mock(name='logger')
        self.mock_elastic_search = Mock(name='elastic_search')
        self.mock_bucket = dict(
            elastic_search=self.mock_elastic_search,
            environment=self.tahoe.environment)
        self.mock_query = Mock(name='query')
        self.mock_filter = Mock(name='filter')
        self.mock_query.filter = self.mock_filter

        class ModelClass(object):
            query = self.mock_query

        self.mock_db = Mock(name='db')
        self.mock_db.Model = ModelClass

        ModelRegistry.destroy_all()

    def test_searchable_mixin(self):
        """
        SearchableMixin: Mixin works and adds all the right methods
        """
        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert 'TestModel' in mr.models
        assert mr.TestModel

        assert self.mock_db.Column.call_count == 0
        assert hasattr(mr.TestModel, 'query')

        assert hasattr(mr.TestModel, '_search_geo_configure')
        assert hasattr(mr.TestModel, '_search_geo_annotate_distance')
        assert hasattr(mr.TestModel, 'search')
        assert hasattr(mr.TestModel, '_search_doc_type')
        assert hasattr(mr.TestModel, '_search_index_alias')
        assert hasattr(mr.TestModel, '_search_index_name')
        assert hasattr(mr.TestModel, '_search_index')
        assert hasattr(mr.TestModel, '_search_create_index')
        assert hasattr(mr.TestModel, '_search_index_all_records')

        tm = mr.TestModel()

        assert hasattr(tm, 'index')
        assert hasattr(tm, 'can_index')
        assert hasattr(tm, 'remove_from_index')

    def test_searchable_geo_configure_without_latlng(self):
        """
        SearchableMixin: Geographical search doesn't happen unless lat/lng as specified
        """
        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert 'TestModel' in mr.models
        assert mr.TestModel

        assert self.mock_db.Column.call_count == 0
        assert hasattr(mr.TestModel, 'query')

        search_terms = dict(sorted_by='distance')
        distance = 10
        filters = Mock(name='search_filters')
        sort = Mock(name='sort')

        assert hasattr(mr.TestModel, '_search_geo_configure')
        sort, geo_search = mr.TestModel._search_geo_configure(
            search_terms,
            distance,
            filters,
            sort)

        assert not geo_search
        assert not isinstance(sort, list)
        assert not filters.append.called

    def test_searchable_geo_configure_with_latlng(self):
        """
        SearchableMixin: A query can be configured happen with a geographical centerpoint and radius
        """
        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert 'TestModel' in mr.models
        assert mr.TestModel

        assert self.mock_db.Column.call_count == 0
        assert hasattr(mr.TestModel, 'query')

        mock_lat = '-47.2929302983'
        mock_lng = '37.928392939'
        search_terms = dict(
            lat=mock_lat,
            lng=mock_lng,
            sorted_by='distance')
        distance = 10
        filters = Mock(name='search_filters')
        sort = Mock(name='sort')
        geo_filter = Mock(name="geo_filter")

        assert hasattr(mr.TestModel, '_search_geo_configure')
        sort, geo_search = mr.TestModel._search_geo_configure(
            search_terms,
            distance,
            filters,
            sort,
            geo_filter=geo_filter)

        assert geo_search
        assert filters.append.called
        geo_filter.assert_called_once_with(
            'location',
            "{},{}".format(mock_lat, mock_lng),
            distance,
            distance_type='arc',
            distance_unit='km')

        assert isinstance(sort, list)
        assert len(sort) == 1
        geo_distance_sort = sort[0].get('_geo_distance')
        assert geo_distance_sort
        assert geo_distance_sort.get('location') == "{},{}".format(mock_lat, mock_lng)
        assert geo_distance_sort.get('order') == 'asc'
        assert geo_distance_sort.get('unit') == 'km'

    def test_search_geo_annotate(self):
        """
        SearchableMixin: Results can be annotated with their geographical distance
        """
        class Meta(object):
            def __init__(self, distance):
                self.sort = [distance]

        class Result(dict):
            def __init__(self, distance):
                self._meta = Meta(distance)

        distances = [1, 1, 2, 3, 5, 8, 13]
        results = []
        for d in distances:
            results.append(Result(d))

        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()

        assert hasattr(mr.TestModel, '_search_geo_annotate_distance')
        mr.TestModel._search_geo_annotate_distance(results)

        for idx, result in enumerate(results):
            assert result.get('distance') == distances[idx]
            assert result.get('distance_unit') == 'km'

    def test_search_doc_type(self):
        """
        SearchableMixin: Model document type is the name of the model
        """
        ModelRegistry.register()(self.make_callback())
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModel, '_search_doc_type')
        assert mr.TestModel._search_doc_type() == 'TestModel'

    def test_search_index_alias(self):
        """
        SearchableMixin: Model index alias contains the model name and environment
        """
        ModelRegistry.register()(self.make_callback())

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModel, '_search_index_alias')
        assert 'TestModel'.lower() in mr.TestModel._search_index_alias()
        assert self.tahoe.environment in mr.TestModel._search_index_alias()

    def test_search_index(self):
        """
        SearchableMixin: Model can return search index settings
        """
        ModelRegistry.register()(self.make_callback())

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModel, '_search_index')
        si = mr.TestModel._search_index()
        assert si
        settings = si.get('settings')
        mappings = si.get('mappings')
        assert settings and mappings
        assert settings == search.STANDARD_SETTINGS
        tm_mapping = mappings.get(mr.TestModel._search_doc_type())
        assert tm_mapping

    def test_search_index_name(self):
        """
        SearchableMixin: Model can return search index name
        """
        ModelRegistry.register()(self.make_callback())
        suffix = "1234567890"
        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModel, '_search_index_name')
        index_name = mr.TestModel._search_index_name(suffix)
        assert index_name
        assert index_name.endswith(suffix)
        assert mr.TestModel._search_index_alias() in index_name

    def test_unconfigured_builder_mapping_and_index(self):
        """
        SearchableMixin: Model throws not implemented error if the mapping or index is not defined
        """
        ModelRegistry.register()(self.make_callback(bad=True))

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModelBad, '_search_builder_mapping')
        assert hasattr(mr.TestModelBad, '_search_index_mapping')
        with self.assertRaises(NotImplementedError):
            mr.TestModelBad._search_builder_mapping()
        with self.assertRaises(NotImplementedError):
            mr.TestModelBad._search_index_mapping()

    def test_search_create_index(self):
        """
        SearchableMixin: Can create index
        """
        suffix = '1234567890'
        ModelRegistry.register()(self.make_callback())

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()
        assert hasattr(mr.TestModel, '_search_create_index')
        index_name = mr.TestModel._search_index_name(suffix=suffix)
        index_settings = mr.TestModel._search_index().get('settings')
        mapping = mr.TestModel._search_index_mapping()
        doc_type = mr.TestModel._search_doc_type()
        mr.TestModel._search_create_index(suffix=suffix)

        assert self.mock_logger.info.call_count == 2

        self.mock_elastic_search.indices.delete_index_if_exists.assert_called_once_with(index_name)
        self.mock_elastic_search.indices.create_index.assert_called_once_with(
            index_name,
            settings=index_settings)
        self.mock_elastic_search.indices.put_mapping.assert_called_once_with(
            doc_type,
            mapping,
            [index_name])
