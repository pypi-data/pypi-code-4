import random
from pmxbot import storage
import pmxbot
import re


def init_models():
    HaikusSevens.initialize()
    HaikusFives.initialize()


class Haikus(storage.SelectableStorage):
    lib = 'pmx'

    @classmethod
    def initialize(cls):
        cls.store = cls.from_URI(pmxbot.config.database)
        cls._finalizers.append(cls.finalize)

    @classmethod
    def finalize(cls):
        del cls.store


class MongoDBHaikus(Haikus, storage.MongoDBStorage):

    def lookup_num(self, rest=''):
        rest = rest.strip()
        if rest:
            if rest.split()[-1].isdigit():
                num = rest.split()[-1]
                query = ' '.join(rest.split()[:-1])
                qt, i, n = self.quoteLookup(query, num)
            else:
                qt, i, n = self.quoteLookup(rest)
        else:
            qt, i, n = self.quoteLookup()
        return qt, i, n

    def _make_term_pattern(self, term):
        return re.compile(term, re.I)

    def _make_results(self):
#        if regex:
#            pattern = self._make_term_pattern(regex)
#            find_opts = dict(library=self.lib)
#            return  [
#                row['text'] for row in
#                self.db.find(find_opts).sort('_id')
#                if pattern.search(row['text'])
#            ]
#
        # have tried with 'text' in find_opts but not dice
        # this obviously doesn't work. Lets ping jaraco :(
#        if regex:
#            find_opts = {'message': {'$regex': self._make_term_pattern(regex)}}
#            #find_opts = {'library': self.lib,
#            #             'message': {'$regex': self._make_term_pattern(regex)}}
        find_opts = dict(library=self.lib)
        return [
            row['text'] for row in
            self.db.find(find_opts).sort('_id')
        ]

    def get_one(self, about=None):
        results = self._make_results()
        if not len(results) and not about:
            return ''
        if about:
            pattern = self._make_term_pattern(about)
            pattern_results = [i for i in results if pattern.search(i)]
            if len(pattern_results):
                results = pattern_results

        total = len(results)
        random_index = random.randrange(total)
        return results[random_index]

    def lookup(self, thing='', num=0):
        thing = thing.strip().lower()
        num = int(num)
        words = thing.split()

        def matches(quote):
            quote = quote.lower()
            return all(word in quote for word in words)
        results = [
            row['text'] for row in
            self.db.find(dict(library=self.lib)).sort('_id')
            if matches(row['text'])
        ]
        n = len(results)
        if n > 0:
            if num:
                i = num - 1
            else:
                i = random.randrange(n)
            quote = results[i]
        else:
            i = 0
            quote = ''
        return (quote, i + 1, n)

    def add(self, quote):
        quote = quote.strip()
        quote_id = self.db.insert(dict(library=self.lib, text=quote))
        # see if the quote added is in the last IRC message logged
        newest_first = [('_id', storage.pymongo.DESCENDING)]
        last_message = self.db.database.logs.find_one(sort=newest_first)
        if last_message and quote in last_message['message']:
            self.db.update({'_id': quote_id},
                           {'$set': dict(log_id=last_message['_id'])})

    def __iter__(self):
        return self.db.find(library=self.lib)

    def _build_log_id_map(self):
        from . import logging
        if not hasattr(logging.Logger, 'log_id_map'):
            log_db = self.db.database.logs
            logging.Logger.log_id_map = dict(
                (logging.MongoDBLogger.extract_legacy_id(rec['_id']), rec['_id'])
                for rec in log_db.find(fields=[])
            )
        return logging.Logger.log_id_map

    def import_(self, quote):
        log_id_map = self._build_log_id_map()
        log_id = quote.pop('log_id', None)
        log_id = log_id_map.get(log_id, log_id)
        if log_id is not None:
            quote['log_id'] = log_id
        self.db.insert(quote)


class HaikusSevens(MongoDBHaikus):

    collection_name = 'haikus_sevens'


class HaikusFives(MongoDBHaikus):

    collection_name = 'haikus_fives'
