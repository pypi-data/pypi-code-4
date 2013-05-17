ADMINS = (
    ("loci", "opensource@jensnistler.de"),
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "yourSecretKey"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_auth.backends.contrib.github.GithubBackend",
)

SOCIAL_AUTH_ENABLED_BACKENDS = ("github",)

GITHUB_APP_ID = "4e45a0b10ab67df21571"
GITHUB_API_SECRET = "3f09a44e1ad1c8bb15f60525214705776a7f6588"


