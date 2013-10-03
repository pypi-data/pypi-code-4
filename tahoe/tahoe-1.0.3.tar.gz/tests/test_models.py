from tahoe.models import ModelRegistry
from tahoe.tests import TahoeTestCase
from mock import Mock


class TestModel(object):
    @classmethod
    def set_args(cls, args):
        cls.args = args

    @classmethod
    def set_kwargs(cls, kwargs):
        cls.kwargs = kwargs

    @classmethod
    def destroy(cls):
        cls.args = None
        cls.kwargs = None


class TestFoo(TestModel):
    pass


class TestBar(TestModel):
    pass

test_models = [TestFoo, TestBar]


def make_callback(test_model):
    def callback(*callback_args, **callback_kwargs):
        test_model.set_args(callback_args)
        test_model.set_kwargs(callback_kwargs)
        return test_model
    return callback


class TestModels(TahoeTestCase):
    def setUp(self):
        self.mock_config = Mock(name='config')
        self.mock_db = Mock(name='db')
        self.mock_app = Mock(name='app')
        self.mock_logger = Mock(name='logger')
        self.mock_bucket = Mock(name='bucket')

    def tearDown(self):
        ModelRegistry.destroy_all()
        for test_model in test_models:
            test_model.destroy()

    def test_registering_a_model(self):
        """
        Can register a callback
        """
        before_callbacks = len(ModelRegistry.model_callbacks)
        before_models = len(ModelRegistry.models)

        test_model = test_models[0]
        callback = make_callback(test_model)
        ModelRegistry.register()(callback)

        after_callbacks = len(ModelRegistry.model_callbacks)
        after_models = len(ModelRegistry.models)

        assert after_callbacks == before_callbacks + 1
        assert callback in ModelRegistry.model_callbacks
        assert after_models == before_models

    def test_setup_model(self):
        """
        Model can be setup as needed
        """
        before_models = len(ModelRegistry.models)

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)

        test_model = test_models[1]
        callback = make_callback(test_model)
        model_name, model_class = mr._setup_model(callback)

        after_models = len(ModelRegistry.models)

        assert after_models == before_models
        assert model_class == test_model
        assert model_name == test_model.__name__

        assert model_class.kwargs['models'] == mr
        assert model_class.kwargs['app'] == self.mock_app
        assert model_class.kwargs['config'] == self.mock_config
        assert model_class.kwargs['db'] == self.mock_db
        assert model_class.kwargs['logger'] == self.mock_logger
        assert model_class.kwargs['bucket'] == self.mock_bucket

    def test_setup_and_add_model(self):
        """
        Model Class has app-level instances in scope when callback is setup
        """
        ModelRegistry.destroy_all()

        assert len(ModelRegistry.models) == 0
        test_model = TestFoo
        callback = make_callback(test_model)

        ModelRegistry.register()(callback)

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()

        assert len(ModelRegistry.models) == 1
        assert 'TestFoo' in ModelRegistry.models
        assert 'TestFoo' in mr.models
        assert mr.TestFoo

        TF = mr.TestFoo

        assert TF.kwargs['models'] == mr
        assert TF.kwargs['app'] == self.mock_app
        assert TF.kwargs['config'] == self.mock_config
        assert TF.kwargs['db'] == self.mock_db
        assert TF.kwargs['logger'] == self.mock_logger
        assert TF.kwargs['bucket'] == self.mock_bucket

    def test_nonexistant_model_raises_exception(self):
        """
        Attempting to access a model that isn't register raises ValueError
        """
        ModelRegistry.destroy_all()

        assert len(ModelRegistry.models) == 0
        test_model = TestFoo
        callback = make_callback(test_model)

        ModelRegistry.register()(callback)

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)
        mr.setup()

        assert mr.TestFoo

        with self.assertRaises(ValueError):
            mr.TestBar

    def test_registry_repr_includes_all_setup_models(self):
        """
        Setting up a model causes it to show in the repr for the registry.
        """
        ModelRegistry.destroy_all()

        assert len(ModelRegistry.models) == 0
        test_model = TestFoo
        callback = make_callback(test_model)

        ModelRegistry.register()(callback)

        mr = ModelRegistry(
            app=self.mock_app,
            config=self.mock_config,
            db=self.mock_db,
            logger=self.mock_logger,
            bucket=self.mock_bucket)

        assert 'TestFoo' not in str(mr)
        assert 'TestBar' not in str(mr)

        mr.setup()

        assert 'TestFoo' in str(mr)
        assert 'TestBar' not in str(mr)
