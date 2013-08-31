import bobo
import zc.wsgidriver

@bobo.query("/")
def blank(title='test title', content='test content'):
    return zc.wsgidriver.html(
        scripts = [
            """
            wsgidriver_x = 1;
            """,
            "/test.js",
            """<script type="text/javascript">
            wsgidriver_y = 2;
            </script>
            """
            ],
        css = ['/test.css'],
        title = title,
        body="<body>%s</body>" % content
        )

@bobo.query("/test.js", content_type="application/javascript")
def js():
    return 'wsgidriver_z = 3'

@bobo.query("/test.css", content_type="text/css")
def css():
    return 'body {color: #999; }'

app = bobo.Application(bobo_resources=__name__)

def test_suite():
    return zc.wsgidriver.TestSuite('example.rst', app=app)

