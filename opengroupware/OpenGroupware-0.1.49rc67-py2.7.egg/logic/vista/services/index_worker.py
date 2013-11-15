#
# Copyright (c) 2011, 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import uuid
import traceback
import multiprocessing
from datetime import datetime, timedelta
from coils.core import MultiProcessWorker, AdministrativeContext
from orm import SearchVector
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError
from edition import INDEXER_EDITION

from index_company import index_contact, index_enterprise
from index_document import index_document
from index_note import index_note
from index_task import index_task
from index_project import index_project

from events import \
    VISTA_VECTOR_REFRESHED, \
    VISTA_VECTOR_CURRENT, \
    VISTA_INVALID_ENTITY, \
    VISTA_VECTOR_ERROR_UNICODE, \
    VISTA_VECTOR_ERROR_ACCESS, \
    VISTA_VECTOR_ERROR_OTHER, \
    VISTA_UNSUPPORTED_ENTITY, \
    VISTA_MISSING_ENTITY, \
    VISTA_INDEX_REQUEST, \
    VISTA_VECTOR_ERROR_INTEGRITY, \
    VISTA_INDEX_EXPUNGE


class VistaWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, ):
        MultiProcessWorker.__init__(self, name, work_queue, event_queue, )
        self.context = AdministrativeContext()

    def process_worker_message(self, command, payload):
        try:
            object_id = long(payload)
        except Exception as e:
            self.log.exception(e)
        else:
            if command == VISTA_INDEX_REQUEST:
                self.refresh_entity_index(object_id)
            elif command == VISTA_INDEX_EXPUNGE:
                self.expunge_entity_from_index(object_id)

    def refresh_entity_index(self, object_id):

        entity = self.context.type_manager.\
            get_entity(object_id, repair_enabled=True, )

        try:
            if entity:
                if (
                    not hasattr(self,
                                '_index_{0}'.format(
                                    entity.__entityName__.lower()))
                ):
                    self.log.debug(
                        'Entity type {0} not supported by index.'.
                        format(entity.__entityName__, ))
                    self.enqueue_event(
                        VISTA_UNSUPPORTED_ENTITY,
                        (object_id,
                         entity.__entityName__, ),
                    )
                    return
            else:
                self.log.debug(
                    'Cannot marshal objectId#{0}'.format(object_id, ))
                self.enqueue_event(VISTA_MISSING_ENTITY, (object_id, ), )
                return
        except Exception as exc:
            self.log.exception(exc)
            return

        db = self.context.db_session()

        vector_entry = None
        try:
            query = db.query(SearchVector).\
                filter(SearchVector.object_id == object_id).\
                with_lockmode('update')
            vector_entry = query.one()
        except NoResultFound:
            self.log.debug(
                'Creating new search vector for objectId#{0}/{1}'.
                format(object_id, entity.__entityName__, ))
            vector_entry = SearchVector(entity.object_id,
                                        entity.__entityName__,
                                        entity.version,
                                        INDEXER_EDITION, )
            self.context.db_session().add(vector_entry)
        except MultipleResultsFound:
            self.event_queue.put(
                (VISTA_VECTOR_ERROR_OTHER,
                 (object_id,
                  entity.__entityName__,
                  traceback.format_exc(), ), )
            )
        except Exception as exc:
            self.log.error('An unexcepted exception has occurred')
            self.log.exception(exc)
            self.event_queue.put(
                (VISTA_VECTOR_ERROR_OTHER,
                 (object_id,
                  entity.__entityName__,
                  traceback.format_exc(), ), )
            )
        else:
            self.log.debug(
                'Found search vector for objectId#{0}'.
                format(entity.object_id, ))
            if (
                (vector_entry.version == entity.version) and
                (vector_entry.edition == INDEXER_EDITION)
            ):
                self.log.debug(
                    'Search index for objectId#{0} is current'.
                    format(entity.object_id, ))
                self.enqueue_event(VISTA_VECTOR_CURRENT, (object_id, ), )
                vector_entry = None
            else:
                self.log.debug(
                    'Search vector for objectId#{0} is version {1}, entity '
                    'is version {2}; updating'.
                    format(entity.object_id,
                           vector_entry.version,
                           entity.version, ))
                vector_entry.version = entity.version
                vector_entry.edition = INDEXER_EDITION
        finally:
            if not vector_entry:
                self.context.rollback()
                return
            else:
                try:
                    self.context.flush()
                except IntegrityError:
                    '''
                    Possibly one of the other workers got to it first, so this
                    should have its own event definition, but the *descision
                    of what to do* should be made by the service component,
                    not by the laboring slave.
                    '''
                    self.context.rollback()
                    self.enqueue_event(
                        VISTA_VECTOR_ERROR_INTEGRITY,
                        (object_id,
                         entity.__entityName__,
                         traceback.format_exc(), ),
                    )
                    return
                except:
                    self.context.rollback()
                    self.enqueue_event(
                        VISTA_VECTOR_ERROR_OTHER,
                        (object_id,
                         entity.__entityName__,
                         traceback.format_exc(), ),
                    )
                    return

        method = '_index_{0}'.format(entity.__entityName__.lower(), )
        if hasattr(self, method):
            index_function = getattr(self, method)
        else:
            self.log.error(
                'Index worker has no such method as {0}'.
                format(method, ))
            return

        try:

            if hasattr(entity, 'project_id'):
                vector_entry.project_id = entity.project_id
            else:
                vector_entry.project_id = None

            vector_entry.keywords, \
                vector_entry.archived, \
                vector_entry.event_date, \
                text = index_function(entity)

            vector_entry.vector = func.to_tsvector('english', text)

        except UnicodeEncodeError, e:
            self.log.exception(e)
            self.context.rollback()
            self.enqueue_event(
                VISTA_VECTOR_ERROR_UNICODE,
                (object_id,
                 entity.__entityName__,
                 traceback.format_exc(), ),
            )
        except AttributeError, e:
            self.log.exception(e)
            self.context.rollback()
            self.enqueue_event(
                VISTA_VECTOR_ERROR_ACCESS,
                (object_id,
                 entity.__entityName__,
                 traceback.format_exc(), ),
            )
        except Exception, e:
            self.log.exception(e)
            self.context.rollback()
            self.enqueue_event(
                VISTA_VECTOR_ERROR_OTHER,
                (object_id,
                 entity.__entityName__,
                 traceback.format_exc(), ),
            )

        self.log.info('{0} OK'.format(self.name, ))

        try:
            self.context.commit()
        except IntegrityError:
            '''
            Possibly one of the other workers got to it first, so this should
            have its own event definition, but the *descision of what to do*
            should be made by the service component, not by the laboring slave.
            '''
            self.context.rollback()
            self.enqueue_event(
                VISTA_VECTOR_ERROR_INTEGRITY,
                (object_id,
                 entity.__entityName__,
                 traceback.format_exc(), ),
            )
        except:
            self.context.rollback()
            self.enqueue_event(
                VISTA_VECTOR_ERROR_OTHER,
                (object_id,
                 entity.__entityName__,
                 traceback.format_exc(), ),
            )
        else:
            self.enqueue_event(
                VISTA_VECTOR_REFRESHED,
                (object_id, ),
            )

    def _index_task(self, task):

        return index_task(task=task, context=self.context, )

    def _index_contact(self, contact):

        return index_contact(contact=contact, context=self.context, )

    def _index_enterprise(self, enterprise):

        return index_enterprise(enterprise=enterprise, context=self.context, )

    def _index_document(self, document):

        #return keywords, archived, event_date, stream.getvalue()
        return index_document(document=document, context=self.context, )

    def _index_note(self, note):

        return index_note(note=note, context=self.context, )

    def _index_project(self, project):

        return index_project(project=project, context=self.context, )

    def expunge_entity_from_index(self, object_id):
        db = self.context.db_session()

        try:
            query = db.query(SearchVector).\
                filter(SearchVector.object_id == object_id).\
                with_lockmode('update')
            self.log.debug(
                '{0} entities expunged from vista index.'.
                format(query.delete(), ))
            self.context.commit()
        except Exception as exc:
            self.log.error(
                'An exception has occured expunging vista index entries '
                'for OGo#{0}'.format(object_id, ))
            self.log.exception(exc)
            self.context.rollback()
        '''
        Currently this does not post any confirmation back to the service
        work queue
        '''
        return
