# -*- coding: utf-8 -*-

import pymongo
import motor
from tornado import gen
from tornado.ioloop import IOLoop

class MySONManipulator(pymongo.son_manipulator.SONManipulator):
    def transform_incoming(self, son, collection):
        return son

def test_pymongo():
    client = pymongo.MongoClient()
    db = client['test']
    db.add_son_manipulator(MySONManipulator())
    collection = db['test']

    collection.remove()
    collection.insert({'name': 'a'})
    collection.update({'name': 'a'}, {'word': 'hello world'}, manipulate=True)
    print collection.find_one()

client = motor.MotorClient().open_sync()
db = client['test']
db.add_son_manipulator(MySONManipulator())
collection = db['test']

# 1. 名字不能含有.和$
# 1. pure document和操作符不能混合使用
# 
@gen.coroutine
def test():
    yield collection.remove()
    # object_id = yield collection.insert(
                    # {'name': 'lime', 'sex': 'male', 'age': 23})

    # result = yield collection.update(
                    # {'name': 'bob'}, {'$set': {'gf': 'me'}, '$inc': {'age': 1}, '$rename': {'namexx': 'nnnnn'}},
                    # upsert=True)

    result = yield collection.update(
                    {'hello.xx': {'a': 3}, 'hello.xx': {'a': 4}}, {
                    # '$set': {'name': 'me'}, 
                    '$inc': {'age': 1}, 
                    # '$rename': {'namexx': 'nnnnn'}, 
                    # '$unset': {'name': 'alice'},
                    '$addToSet': {'skill': {'$each': ['python', 'tornado'] }},
                    # '$setOnInsert':{'wtf': 100},
                    # '$pop': {'what': 1},
                    # '$pullAll': {'hello': ['1', 2] },
                    # '$pull': {'hello1': 2},
                    '$pushAll': {'book': [1, 2] },
                    '$push': {'books': {'$each': [3, 4], 
                                       '$slice': -7, 
                                       '$sort':{'book': 1}}},
                    # '$bit': {'nima': {'or': 4}}
                    },
                    upsert=True)

    result = yield collection.find().to_list(10)
    print result
    raise gen.Return(result)


@gen.coroutine
def test_motor():
    client = motor.MotorClient().open_sync()
    db = client['test']
    db.add_son_manipulator(MySONManipulator())
    collection = db['test']
    
    yield collection.remove()
    yield collection.insert({'name': 'shiyanhui', 'books': {'name': 'yes', 'pages': 200}})
    result = yield collection.find_one({'name': 'shiyanhui'})
    print result
    yield collection.update({'name': 'shiyanhui'}, {'$unset': {'book.name': 1} })
    result = yield collection.find_one() 
    print result

if __name__ == '__main__':
    IOLoop.current().run_sync(test_motor)
