AX_FIRST_NAME = "first_name"
AX_LAST_NAME = "last_name"
AX_EMAIL = "email"
AX_ZIPCODE = "zip_code"
AX_OLDPASSWD = "old_password"
AX_NEWPASSWD = "new_password"
AX_IS_VERIFIED = "is_verified"

AX_MAPPINGS = {
    AX_FIRST_NAME: [
        'http://openid.net/schema/namePerson/first',
        'http://axschema.org/namePerson/first'
    ],
    AX_LAST_NAME: [
        'http://openid.net/schema/namePerson/last',
        'http://axschema.org/namePerson/last'
    ],
    AX_EMAIL: [
        'http://openid.net/schema/contact/internet/email',
        'http://axschema.org/contact/email'
    ],
    AX_ZIPCODE: [
        'http://openid.net/schema/contact/postalcode/home',
        'http://axschema.org/contact/postalCode/home'
    ],
    AX_OLDPASSWD: [
        'https://account.pbs.org/cranky/ax/old_password',
    ],
    AX_NEWPASSWD: [
        'https://account.pbs.org/cranky/ax/new_password',
    ],
    AX_IS_VERIFIED: [
        'https://account.pbs.org/cranky/ax/is_verified',
    ],
}
