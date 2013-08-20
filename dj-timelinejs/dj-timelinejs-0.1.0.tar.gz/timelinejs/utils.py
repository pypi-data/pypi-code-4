import re

MAX_URL_LENGTH = 35
TRAILING_URL_LENGTH = 6
SHORTENED_URL_PLACEHOLDER = "..."

def get_link_matches(text):
    re_text = r'(?i)\b(?<!..]\(|\d]:\s)((?:https?://|(?<!:\/\/)www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))'
    matcher = re.compile(re_text)
    return matcher.findall(text)

def markdown_linkify(text):
    """
    Preprocessor to add links to markdown.
    """
    for match in get_link_matches(text):
        url = match[0]
        # add http:// in front of links without it
        if url[:4] != "http":
            href = "http://" + url
        else:
            href = url
        # shorten the link_text if necessary
        if len(url) > MAX_URL_LENGTH:
            link_text = url[:MAX_URL_LENGTH - (TRAILING_URL_LENGTH + len(SHORTENED_URL_PLACEHOLDER))] + SHORTENED_URL_PLACEHOLDER + url[-TRAILING_URL_LENGTH:]
        else:
            link_text = url
        text = text.replace(url, "[%s](%s)" % (link_text, href))
    return text
