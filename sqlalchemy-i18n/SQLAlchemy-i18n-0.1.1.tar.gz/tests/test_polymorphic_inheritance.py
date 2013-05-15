import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestPolymorphicInheritance(TestCase):
    def create_models(self):
        class TextItem(self.Model, Translatable):
            __tablename__ = 'text_item'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'locale_getter': lambda: 'en'
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            discriminator = sa.Column(
                sa.Unicode(100)
            )
            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

        class Article(TextItem):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )
            __translated_columns__ = [
                sa.Column('caption', sa.UnicodeText)
            ]
            __mapper_args__ = {'polymorphic_identity': u'article'}
            category = sa.Unicode(255)

        self.TextItem = TextItem
        self.Article = Article

    def test_auto_creates_relations(self):
        textitem = self.TextItem()
        assert textitem.translations
        assert textitem._translations
        article = self.Article()
        assert article.translations
        assert article._translations

    def test_auto_creates_current_translation(self):
        textitem = self.TextItem()
        assert textitem.current_translation
        article = self.Article()
        assert article.current_translation

    def test_translatable_attributes(self):
        textitem = self.TextItem()
        assert textitem.__translatable__['class']
        article = self.Article()
        assert article.__translatable__['class']

    def test_translated_columns(self):
        article = self.Article()
        columns = article.__translatable__['class'].__table__.c
        assert 'caption' in columns
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns
