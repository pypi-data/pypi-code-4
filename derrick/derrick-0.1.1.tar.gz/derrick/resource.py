import glob
import json
import mimetypes
import os

from twisted.web.resource import Resource


FAVICON = 'GIF89a\x01\x00\x01\x00\xf0\x00\x00\xff\xff\xff\x00\x00\x00!' \
          '\xff\x0bXMP DataXMP\x02?x\x00!\xf9\x04\x05\x00\x00\x00\x00,' \
          '\x00\x00\x00\x00\x01\x00\x01\x00@\x02\x02D\x01\x00;'


class DerrickRootResource(Resource):
    '''The root resource for serving Impact.js games via Derrick.

    Since Impact.js has hardcoded url paths, there are specific urls that are
    expected, and then it can fall through to static files.
    '''

    isLeaf = True

    blacklist = ['tools']

    def __init__(self, root='.'):
        self.root = os.path.realpath(root)

    def _is_safe(self, filename):
        '''Test filenames for security/safety.'''
        filename = os.path.realpath(filename)
        return os.path.commonprefix([filename, self.root]) == self.root

    def _save(self, request):
        '''Save the Weltmeister level.

        Form data contains two fields: path and data. The path is the filepath
        location to save the level content. The data field is the actual
        content of the level (which is just ImpactJS javascript.
        '''
        path = request.args.get('path', None)
        data = request.args.get('data', None)
        if not path or not data:
            request.setResponseCode(503)
            return json.dumps({'error': 1, 'msg': 'No data or path'})

        path = path[0]
        if self._is_safe(path):
            open(path, 'w').write(data[0])
            request.setResponseCode(200)
            return json.dumps({'error': 0})
        else:
            request.setResponseCode(403)
            return ''

    def _browse(self, request):
        '''Return a json object containing a directory listing.

        A single GET parameter pointing to a directory is provided, and its
        directory listing is returned in a json format.

        The javascript object looks like this:

        {
            files: ['lib/game/levels/levelOne.js', 'lib/game/levels/levelTwo.js'],
            dirs: [],
            parent: 'lib/game'
        }
        '''
        top_dir = request.args.get('dir')
        if not top_dir:
            request.setResponseCode(404)
            return ''

        top_dir = top_dir[0]
        if not self._is_safe(top_dir):
            request.setResponseCode(404)
            return ''
        dirs = [os.path.join(top_dir, d)
                for d in os.listdir(os.path.join(self.root, top_dir))
                if os.path.isdir(os.path.join(top_dir, d))]
        files = glob.glob(os.path.join(top_dir, '*.*'))

        if 'type' in request.args:
            types = request.args.get('type')[0]
            if 'scripts' in types:
                files = [f for f in files if os.path.splitext(f)[1] == '.js']

        request.setResponseCode(200)
        return json.dumps({
            'files': files,
            'dirs': dirs,
            'parent': False if top_dir == './' else os.path.dirname(top_dir)
        })

    def _glob(self, request):
        '''Translate glob paths to json paths.

        A single GET parameter named glob[] should contain a list of
        directories. Return a json list of all files matching those globs.
        '''
        globs = request.args.get('glob[]', None)
        if not globs:
            request.setResponseCode(503)
            return 'globs[] not set'

        files = []
        for _glob in globs:
            if self._is_safe(_glob):
                _files = glob.glob(_glob)
                files.extend(_files)
        return json.dumps(files)

    def render_GET(self, request):
        '''Handle GET request (Duh).

        There are a few hardcoded urls here that require explanation:

        / - Return the index page
        /editor - Return the weltmeister level editor
        /lib/weltmeister/api/glob.php - See `DerrickRootResource._glob`
        /lib/weltmeister/api/browse.php - See `DerrickRootResource._browse`

        Otherwise, return the file referenced, or a 404.
        '''
        path = request.path

        if path == '/':
            path = 'index.html'
        # TODO: this should be a config
        elif path == '/editor':
            path = 'weltmeister.html'
        elif path == '/lib/weltmeister/api/glob.php':
            return self._glob(request)
        elif request.path == '/lib/weltmeister/api/browse.php':
            return self._browse(request)

        # Trim the leading forward slash
        if path[0] == '/':
            path = path[1:]
        for bad in self.blacklist:
            if path.startswith(bad):
                request.setResponseCode(404)
                return ''

        path = os.path.join(self.root, path)
        if not self._is_safe(path):
            request.setResponseCode(404)
            return ''

        try:
            with open(path, 'rb') as f:
                data = f.read()

            content_type = mimetypes.guess_type(path)[0]

            request.setHeader('Content-Type', content_type)
            request.setResponseCode(200)
            return data
        except IOError:
            if 'favicon.ico' in path:
                request.setHeader('Content-Type', 'image/gif')
                request.setResponseCode(200)
                return FAVICON
            else:
                request.setResponseCode(404)
                return None

    def render_POST(self, request):
        '''Handle POST request (Duh).

        There's only one URL that should be handled here, and it's the
        Weltmeister save endpoint.  Take a post with path and data keys, and
        write the data to the provided path.
        '''
        if request.path == '/lib/weltmeister/api/save.php':
            return self._save(request)
        else:
            request.setResponseCode(405)
            return 'Method not allowed'
