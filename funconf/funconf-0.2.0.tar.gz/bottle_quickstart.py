from bottle import route, run
import begin
import funconf

@route('/hello')
def hello():
    return "Hello World!"

config = funconf.Config('webapp.conf')

@begin.start
@config.web
def main(host='127.0.0.1', port=8080, debug=True):
    run(host=host, port=port, debug=debug)
