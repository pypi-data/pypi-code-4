
from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

from cubicweb.dataimport import SQLGenObjectStore

from cubes.semnews.entities.external_resources import (ACCEPTABLE_TYPES,
                                                       query_dbpedia_types)


def _init_cw_connection(appid):
    config = cwconfig.instance_configuration(appid)
    sourcescfg = config.sources()
    config.set_sources_mode(('system',))
    cnx = repo = None
    while cnx is None:
        try:
            login = sourcescfg['admin']['login']
            pwd = sourcescfg['admin']['password']
        except KeyError:
            login, pwd = manager_userpasswd()
        try:
            repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
        except AuthenticationError:
            print 'wrong user/password'
        else:
            break
    session = repo._get_session(cnx.sessionid)
    return cnx, session

def cleanup_ner(session):
    exturis = session.execute('Any X WHERE X is ExternalUri, X activated TRUE')
    deasactivated = set()
    for exturi in exturis.entities():
        # Get dbpedia type
        print '---->', exturi.uri
        types = query_dbpedia_types(exturi.uri)
        if not len(types.intersection(ACCEPTABLE_TYPES)):
            print types
            print '---> DESACTIVATE !'
            deasactivated.add(exturi.eid)
    print 'Desactivating %s external uris' % len(deasactivated)
    for eid in deasactivated:
        session.execute('SET X activated FALSE WHERE X eid %(e)s', {'e': eid})
    session.commit()


class SemnewsCleanUpNER(Command):
    """
    Command for cleaning up NER external uris
    """
    arguments = '<instance>'
    name = 'cleanup-ner'

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        cleanup_ner(session)


class SemnewsProcessNERArticle(Command):
    """
    Command for processing NER in Semnews
    """
    arguments = '<instance>'
    name = 'process-ner'

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        store = SQLGenObjectStore(session)
        ner_processes = list(session.execute('Any X WHERE X is NerProcess').entities())
        _recognized_cache = {}
        current_uris = dict(session.execute('Any U,X WHERE X is ExternalUri, X uri U'))
        for ind, article in enumerate(session.execute('Any N WHERE N is IN (NewsArticle, Tweet)').entities()):
            lang = article.source[0].lang or 'fr'
            processes = sorted([p for p in ner_processes
                                if p.eid not in (e.eid for e in article.processed_by)]
                               , key=lambda x: x.lang==lang)
            if not processes:
                continue
            # NER
            article_content = article.cw_adapt_to('INamedEntitiesContent')
            named_entities = article_content.recognized_entities(processes, token_max_size=5)
            # Store results
            for process in processes:
                store.relate(article.eid, 'processed_by', process.eid)
            seen_uris = set([r[0] for r in session.execute('Any U WHERE X eid %(e)s, '
                                                           'X recognized_entities E, E uri U',
                                                           {'e': article.eid})])
            for uri, process_eid in named_entities:
                print '-->', uri.encode('utf-8')
                if uri in current_uris:
                    current_uri_eid = current_uris[uri]
                else:
                    current_uri_eid = store.create_entity('ExternalUri',
                                                          activated=True,
                                                          cwuri=unicode(uri),
                                                          uri=unicode(uri)).eid
                    current_uris[uri] = current_uri_eid
                if uri not in seen_uris:
                    store.relate(article.eid, 'recognized_entities', current_uri_eid)
                    seen_uris.add(uri)
            if ind and ind % 100 == 0:
                try:
                    store.flush()
                except:
                    return
        # Final flush
        store.flush()
        store.commit()


CWCTL.register(SemnewsProcessNERArticle)
CWCTL.register(SemnewsCleanUpNER)
