from multiprocessing import Process

import requests

import cbmock


class MockHelper(object):

    def __init__(self):
        self.mock = Process(target=cbmock.main, kwargs={"num_nodes": 1})
        self.mock.start()

    def __del__(self):
        self.mock.terminate()

    def train_seriesly(self):
        dbs = ["ns_serverEastdefaultec2-54-242-160-13compute-1amazonawscom",
               "ns_serverEastdefault"]
        for db in dbs:
            params = {
                "path": "/{0}/_query".format(db), "method": "GET",
                "response_code": "200", "response_body": "{}",
            }
            requests.post(url="http://127.0.0.1:8080/", params=params)

    def _submit_sample(self, path, sample):
        base_path = "collectors/fixtures/"
        params = {"method": "GET", "response_code": 200, "path": path}
        with open(base_path + sample) as fh:
            requests.post(url="http://127.0.0.1:8080/", params=params,
                          files={"response_body": fh})
