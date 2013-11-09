
class ScannerTest():
    def test_scanner(self, batch_size=None, start_row=None, end_row=None, start_time=None, end_time=None):
        """
        Creates a scanner instance.

        :return starbase.client.Scanner: Creates and returns a class::`starbase.client.Scanner` instance.
        """
        url = '{0}/scanner'.format(self.name)
        response = HttpRequest(connection=self.connection, url=url, method=PUT).get_response()
        scanner_url = response.raw.headers.get('location')

        column = 'users'
        qualifier = 'email'
        value = 'test@gmail.com'

        single_column_value_filter = {
            "type": "SingleColumnValueFilter",
            "op": "EQUAL",
            "family": base64.b64encode(column),
            "qualifier": base64.b64encode(qualifier),
            "latestVersion": "true",
            "comparator": {
                "type": "BinaryComparator",
                "value": base64.b64encode(value),
            }
        }

        data = json.dumps(single_column_value_filter)


        encode = str(base64.b64encode((value).encode("utf-8")))
        schema= '<Scanner batch ="1" ><filter>' + data + '</filter></Scanner>'
        headers = {
            "Content-length": "",
            "Content-type": "text/xml" + '; charset=UTF-8',
            "Accept": "text/xml"
        }

        return Scanner(table=self, url=scanner_url, data=schema, extra_headers=headers, method=POST)