from authkit.authenticate import middleware, sample_app
from beaker.middleware import SessionMiddleware

app = middleware(
    sample_app,
    setup_method='openid, cookie',
    openid_path_signedin='/private',
    openid_store_type='file',
    openid_store_config='',
    openid_charset='UTF-8',
    cookie_secret='secret encryption string',
    cookie_signoutpath = '/signout',
    # AX options
    openid_ax_typeuri_email='http://openid.net/schema/contact/internet/email',
    openid_ax_required_email=True,
    openid_ax_alias_email='email',
)

app = SessionMiddleware(
    app, 
    key='authkit.open_id', 
    secret='some secret',
)
if __name__ == '__main__':
    from paste.httpserver import serve
    serve(app, host='0.0.0.0', port=8080)
