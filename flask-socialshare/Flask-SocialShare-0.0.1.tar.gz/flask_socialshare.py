try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

def facebook_js():
    return """
<div id="fb-root"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>
"""

def facebook_like_button():
    return """
<div class="fb-like" data-send="false" data-width="450" data-show-faces="true"></div>
"""

def plus_one_js():
    return """
<script type="text/javascript">
  (function() {
    var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
    po.src = 'https://apis.google.com/js/plusone.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
  })();
</script>
"""

def plus_one_button():
    return "<g:plusone></g:plusone>"

def twitter_follow_button(username):
    template = """
<a href="https://twitter.com/{username}" class="twitter-follow-button" data-show-count="false">Follow @{username}</a>
<script>!function(d,s,id){{var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){{js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}}}(document, 'script', 'twitter-wjs');</script>
"""
    return template.format(username=username)

def large_twitter_follow_button(username):
    template = """
<a href="https://twitter.com/{username}" class="twitter-follow-button" data-show-count="false" data-size="large">Follow @{username}</a>
<script>!function(d,s,id){{var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){{js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}}}(document, 'script', 'twitter-wjs');</script>
"""
    return template.format(username=username)

def twitter_tweet(via):
    template = """
<a href="https://twitter.com/share" class="twitter-share-button" data-via="{via}">Tweet</a>
<script>!function(d,s,id){{var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){{js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}}}(document, 'script', 'twitter-wjs');</script>
"""
    return template.format(via=via)

def share_helpers():
    return dict(twitter_follow_button=twitter_follow_button,
                twitter_tweet=twitter_tweet,
                facebook_js=facebook_js,
                facebook_like_button=facebook_like_button,
                plus_one_js=plus_one_js,
                plus_one_button=plus_one_button);
