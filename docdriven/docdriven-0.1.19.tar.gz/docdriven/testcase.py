from _dd_testcase import DocDrivenTestCase


default_base_url='http://216.224.141.220:5438'
default_http_headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
def get_docdriven_testcase(driven_doc, base_url=default_base_url, http_headers=default_http_headers):

    DocDrivenTestCase.remove_test_methods()
    # REMOVE TEST CASES FROM LAST TIME -- EACH INIT SHOULD BE FRESH

    DocDrivenTestCase.driven_doc = driven_doc
    # DocDrivenTestCase.default_base_url = base_url
    # DocDrivenTestCase.default_http_headers = http_headers

    # we dont want a class with no tests, because then
    # the introduction/conclusion won't get run
    def empty_test(self):
        # print 'EMPTY TEST'
        pass
    setattr(DocDrivenTestCase, 'test_empty', empty_test)

    # we add one test method per chapter
    for chapter in DocDrivenTestCase.driven_doc.chapter_list:
        DocDrivenTestCase.insert_test_method(chapter)

    return DocDrivenTestCase
