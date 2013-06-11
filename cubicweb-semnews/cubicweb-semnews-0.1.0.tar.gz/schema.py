# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-semnews schema"""
from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            RichString, String, Int, Float, Date, Boolean)
from cubicweb.schemas.base import CWSource, ExternalUri

## Add lang to source.
CWSource.add_relation(String(), name='lang')
ExternalUri.add_relation(Boolean(default=True, indexed=True), name='activated')


###############################################################################
### DATA ######################################################################
###############################################################################
class NewsArticle(EntityType):
    title = String(maxsize=2048, fulltextindexed=True, indexed=True) # Title of the article
    uri = String(maxsize=1024, unique=True, indexed=True) # Uri of the article
    date = Date(indexed=True)
    content = RichString(fulltextindexed=True) # Content of the feed
    source = SubjectRelation('CWSource', cardinality='?*', inlined=True)
    recognized_entities = SubjectRelation('ExternalUri', cardinality='**')
    processed_by = SubjectRelation('NerProcess', cardinality='**')

class Tweet(EntityType):
    title = String(maxsize=2048, fulltextindexed=True, indexed=True) # Title of the article
    uri = String(maxsize=1024, unique=True, indexed=True) # Uri of the article
    date = Date(indexed=True)
    geo = String(maxsize=256)
    id_str = String(maxsize=128)
    retweet = Int()
    retweeted = Boolean(default=False)
    source = SubjectRelation('CWSource', cardinality='?*', inlined=True)
    recognized_entities = SubjectRelation('ExternalUri', cardinality='**')
    processed_by = SubjectRelation('NerProcess', cardinality='**')
    has_hashtags = SubjectRelation('HashTag', cardinality='**')

class HashTag(EntityType):
    label = String(maxsize=512, indexed=True)
