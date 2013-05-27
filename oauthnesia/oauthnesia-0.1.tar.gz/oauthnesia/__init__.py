from hashlib import sha1
import copy, uuid, time, datetime, operator, urllib2, hmac, binascii, requests, json

class oauthnesia():
    api_base_url = "https://api1.urbanesia.com/"
    api_uri = ""

    consumer_key = ""
    consumer_secret = ""
    user_key = ""
    user_secret = ""

    default_post = {
        'oauth_consumer_key': None,
        'oauth_nonce': None,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': None,
        'oauth_version': '1.0a',
        'safe_encode': 1
    }

    post = {}
    get = {}

    def __init__(self, base_url=None, cons_key=None, cons_sec=None, user_key=None, user_sec=None):
        if base_url:
            self.api_base_url = base_url
        if cons_key:
            self.consumer_key = cons_key
        if cons_sec:
            self.consumer_secret = cons_sec
        if user_key:
            self.user_key = user_key
        if user_sec:
            self.user_secret = user_sec

    def request(self, uri, post=None, get=None):
        if not uri:
            raise Exception("OAUTH requests must include a valid resource URI")
        if not self.consumer_key:
            raise Exception("OAUTH Consumer Key is not initialized properly")
        if not self.consumer_secret:
            raise Exception("OAUTH Consumer Secret is not initialized properly")

        self.api_uri = uri

        default_posts = self.get_default_posts()
        if post is None:
            post = default_posts
        else:
            post.update(default_posts)

        if get is None:
            postget = post
        else:
            postget = copy.deepcopy(post)
            postget.update(get)

        postget_clean = {}
        for (k,v) in postget.iteritems():
            k = urllib2.quote(k.encode("utf8"))
            v = urllib2.quote(str(v).encode("utf8"))
            postget_clean[k] = v
        postget_clean = sorted(postget.iteritems(), key=operator.itemgetter(0))

        base_signature = self.generate_base_signature(postget_clean)
        print base_signature
        signature = self.generate_signature(base_signature, False)

        oauth_sig = "?oauth_signature=%s" % urllib2.quote(signature.encode("utf8"))
        url = "%s%s%s&%s" % (self.api_base_url,
                             self.api_uri, oauth_sig,
                             self.dict_to_string(sorted(get.iteritems(), key=operator.itemgetter(0))))
        print url

        response = requests.post(url, post)
        try:
            return {
                'code': int(response.status_code),
                'data': json.loads(response.content)
            }
        except:
            return {
                'code': 500,
                'data': {'message':'Invalid HTTP Response'}
            }

    def get_default_posts(self):
        p = copy.deepcopy(self.default_post)
        p['oauth_consumer_key'] = self.consumer_key
        p['oauth_nonce'] = self.get_nonce()
        p['oauth_timestamp'] = self.get_time()
        return p

    def get_nonce(self):
        return str(uuid.uuid1()).replace('-', '')

    def get_time(self):
        return int(time.mktime(datetime.datetime.now().timetuple()))

    def generate_base_signature(self, postget):
        return "POST&%s%s&%s" % (urllib2.quote(self.api_base_url.encode("utf8")).replace('/', '%2F'),
                                 urllib2.quote(self.api_uri.encode("utf8")).replace('/', '%2F'),
                                 urllib2.quote(self.dict_to_string(postget).encode("utf8")))

    def generate_signature(self, base_sig, with_user_secret=False):
        if with_user_secret:
            key = "%s&%s" % (self.consumer_secret, self.user_secret)
        else:
            key = "%s&" % self.consumer_secret

        hashed = hmac.new(key, base_sig, sha1)
        arr = binascii.b2a_base64(hashed.digest())
        ret = ""
        for s in arr:
            ret += s
        return ret.replace("\n", "")

    def dict_to_string(self, obj):
        if obj is not None:
            first = True
            ret = ""
            for (k,v) in obj:
                if first:
                    ret += "%s=%s" % (k, v)
                else:
                    ret = "%s&%s=%s" % (ret, k, v)
                first = False
            return ret
        else:
            return ""
