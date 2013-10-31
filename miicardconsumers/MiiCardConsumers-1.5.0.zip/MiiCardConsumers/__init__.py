import json
import httplib2
import oauth2 as oauth
import urllib
import hashlib
from datetime import datetime

class MiiCardServiceUrls(object):
    OAUTH_ENDPOINT = "https://sts.miicard.com/auth/OAuth.ashx"
    CLAIMS_SVC = "https://sts.miicard.com/api/v1/Claims.svc/json"
    FINANCIAL_SVC = "https://sts.miicard.com/api/v1/Financial.svc/json"
    DIRECTORY_SVC = "https://sts.miicard.com/api/v1/Members"

    @staticmethod
    def get_method_url(method_name):
        """[Deprecated] Gets the JSON API endpoint URL for a given method name"""

        return MiiCardServiceUrls.CLAIMS_SVC + "/" + method_name

    @staticmethod
    def get_claims_method_url(method_name):
        """Gets the Claims service JSON API endpoint URL for a given method name"""

        return MiiCardServiceUrls.CLAIMS_SVC + "/" + method_name

    @staticmethod
    def get_financial_method_url(method_name):
        """Gets the Financial service JSON API endpoint URL for a given method name"""

        return MiiCardServiceUrls.FINANCIAL_SVC + "/" + method_name

    @staticmethod
    def get_directory_service_query_url(criterion, value, hashed = False):
        toReturn = MiiCardServiceUrls.DIRECTORY_SVC + "?" + criterion + "=" + value

        if hashed:
            toReturn += "&hashed=true"

        return toReturn

class Claim(object):
    """Base class for verifiable information returned by the miiCard Claims API."""

    def __init__(self, verified):
        self.verified = verified

class Identity(Claim):
    """Represents the user's account details on another website, such as a social media site"""

    def __init__(self, verified, source, user_id, profile_url):
        super(Identity, self).__init__(verified)

        self.source = source
        self.user_id = user_id
        self.profile_url = profile_url

    @staticmethod
    def FromDict(dict):
        """Builds and returns an Identity object from a dictionary of parameters"""

        return Identity(
                        dict.get('Verified', None),
                        dict.get('Source', None),
                        dict.get('UserId', None),
                        dict.get('ProfileUrl', None)
                        )

class EmailAddress(Claim):
    """Represents an email address that the user has linked to their miiCard profile"""

    def __init__(self, verified, display_name, address, is_primary):
        super(EmailAddress, self).__init__(verified)

        self.display_name = display_name
        self.address = address
        self.is_primary = is_primary

    @staticmethod
    def FromDict(dict):
        """Builds and returns an EmailAddress object from a dictionary of parameters"""

        return EmailAddress(
                            dict.get('Verified', None),
                            dict.get('DisplayName', None),
                            dict.get('Address', None),
                            dict.get('IsPrimary', None)
                            )

class PhoneNumber(Claim):
    """Represents a phone number that the user has linked to their miiCard profile"""

    def __init__(self, verified, display_name, country_code, national_number, is_mobile, is_primary):
        super(PhoneNumber, self).__init__(verified)
        
        self.display_name = display_name
        self.country_code = country_code
        self.national_number = national_number
        self.is_mobile = is_mobile
        self.is_primary = is_primary

    @staticmethod
    def FromDict(dict):
        """Builds and returns a PhoneNumber object from a dictionary of parameters"""

        return PhoneNumber(
                           dict.get('Verified', None),
                           dict.get('DisplayName', None),
                           dict.get('CountryCode', None),
                           dict.get('NationalNumber', None),
                           dict.get('IsMobile', None),
                           dict.get('IsPrimary', None)
                           )

class PostalAddress(Claim):
    """Represents a postal address that the user has linked to their miiCard profile"""

    def __init__(self, verified, house, line1, line2, city, region, code, country, is_primary):
        super(PostalAddress, self).__init__(verified)

        self.house = house
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.region = region
        self.code = code
        self.country = country
        self.is_primary = is_primary

    @staticmethod
    def FromDict(dict):
        """Builds and returns a PostalAddress object from a dictionary of parameters"""

        return PostalAddress(
                             dict.get('Verified', None),
                             dict.get('House', None),
                             dict.get('Line1', None),
                             dict.get('Line2', None),
                             dict.get('City', None),
                             dict.get('Region', None),
                             dict.get('Code', None),
                             dict.get('Country', None),
                             dict.get('IsPrimary', None)
                             )

class WebProperty(Claim):
    """Represents a web property such as a domain or website over which the user has demonstrated ownership"""

    def __init__(self, verified, display_name, identifier, type):
        super(WebProperty, self).__init__(verified)

        self.display_name = display_name
        self.identifier = identifier
        self.type = type

    @staticmethod
    def FromDict(dict):
        """Builds and returns a WebProperty object from a dictionary of parameters"""        
        
        return WebProperty(
                           dict.get('Verified', None),
                           dict.get('DisplayName', None),
                           dict.get('Identifier', None),
                           dict.get('Type', None)
                           )

class WebPropertyType(object):
    """Enumerates possible kinds of WebProperty, used by the WebProperty.type field"""

    """Indicates that the WebProperty relates to a domain name"""
    DOMAIN = 0
    """Indicates that the WebProperty relates to a website"""
    WEBSITE = 1

class MiiUserProfile(object):
    """Represents the subset of a miiCard user's identity that they have agreed to share"""

    def __init__(
                 self, 
                 username,
                 salutation,
                 first_name,
                 middle_name,
                 last_name,
                 previous_first_name,
                 previous_middle_name,
                 previous_last_name,
                 last_verified,
                 profile_url,
                 profile_short_url,
                 card_image_url,
                 email_addresses,
                 identities,
                 phone_numbers,
                 postal_addresses,
                 web_properties,
                 identity_assured,
                 has_public_profile,
                 public_profile,
                 date_of_birth,
                 age
                 ):

        self.username = username
        self.salutation = salutation
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.previous_first_name = previous_first_name
        self.previous_middle_name = previous_middle_name
        self.previous_last_name = previous_last_name
        self.last_verified = last_verified
        self.profile_url = profile_url
        self.profile_short_url = profile_short_url
        self.card_image_url = card_image_url
        self.email_addresses = email_addresses
        self.identities = identities
        self.phone_numbers = phone_numbers
        self.postal_addresses = postal_addresses
        self.web_properties = web_properties
        self.identity_assured = identity_assured
        self.has_public_profile = has_public_profile
        self.public_profile = public_profile
        self.date_of_birth = date_of_birth
        self.age = age

    @staticmethod
    def FromDict(dict):
        """Builds and returns a MiiUserProfile object from a dictionary of parameters"""

        emails = dict.get('EmailAddresses', None)
        phone_numbers = dict.get('PhoneNumbers', None)
        postal_addresses = dict.get('PostalAddresses', None)
        identities = dict.get('Identities', None)
        web_properties = dict.get('WebProperties', None)
        public_profile = dict.get('PublicProfile', None)

        if emails:
            emails_parsed = []
            for email in emails:
                emails_parsed.append(EmailAddress.FromDict(email))
        else:
            emails_parsed = None

        if phone_numbers:
            phone_numbers_parsed = []
            for phone_number in phone_numbers:
                phone_numbers_parsed.append(PhoneNumber.FromDict(phone_number))
        else:
           phone_numbers_parsed = None 

        if postal_addresses:
            postal_addresses_parsed = []
            for postal_address in postal_addresses:
                postal_addresses_parsed.append(PostalAddress.FromDict(postal_address))
        else:
            postal_addresses_parsed = None

        if identities:
            identities_parsed = []
            for identity in identities:
                identities_parsed.append(Identity.FromDict(identity))
        else:
            identities_parsed = None

        if web_properties:
            web_properties_parsed = []
            for web_property in web_properties:                 
                web_properties_parsed.append(WebProperty.FromDict(web_property))
        else:
            web_properties_parsed = None

        if public_profile:
            public_profile_parsed = MiiUserProfile.FromDict(public_profile)
        else:
            public_profile_parsed = None

        return MiiUserProfile(
                              dict.get('Username', None),
                              dict.get('Salutation', None),
                              dict.get('FirstName', None),
                              dict.get('MiddleName', None),
                              dict.get('LastName', None),
                              dict.get('PreviousFirstName', None),
                              dict.get('PreviousMiddleName', None),
                              dict.get('PreviousLastName', None),
                              Util.try_parse_datetime_from_json_string(dict.get('LastVerified', None)),
                              dict.get('ProfileUrl', None),
                              dict.get('ProfileShortUrl', None),
                              dict.get('CardImageUrl', None),
                              emails_parsed,
                              identities_parsed,
                              phone_numbers_parsed,
                              postal_addresses_parsed,
                              web_properties_parsed,
                              dict.get('IdentityAssured', None),
                              dict.get('HasPublicProfile', None),
                              public_profile_parsed,
                              Util.try_parse_datetime_from_json_string(dict.get('DateOfBirth', None)),
                              dict.get('Age', None)
                              )

class FinancialRefreshStatus(object):
    """Wraps the state of a financial refresh request"""

    def __init__(
                 self,
                 state
                 ):

        self.state = state

    @staticmethod
    def FromDict(dict):
        """Builds and returns a FinancialRefreshStatus object from a dictionary of parameters"""

        return FinancialRefreshStatus(
                                      dict.get('State', RefreshState.UNKNOWN)
                                      )

class AuthenticationDetails(object):
    """Records the manner of authentication that took place for a given sharing of a miiCard member's identity data"""
    
    def __init__(
                 self,
                 authentication_time_utc,
                 second_factor_token_type,
                 second_factor_provider,
                 locations
                 ):
        
        self.authentication_time_utc = authentication_time_utc
        self.second_factor_token_type = second_factor_token_type
        self.second_factor_provider = second_factor_provider
        self.locations = locations

    @staticmethod
    def FromDict(dict):
        """Builds and returns an AuthenticationDetails object from a dictionary of parameters"""

        locations = dict.get('Locations', None)

        if locations:
            locations_parsed = []
            for location in locations:
                locations_parsed.append(GeographicLocation.FromDict(location))
        else:
            locations_parsed = None

        return AuthenticationDetails(
                                     Util.try_parse_datetime_from_json_string(dict.get('AuthenticationTimeUtc', None)),
                                     dict.get('SecondFactorTokenType', AuthenticationTokenType.NONE),
                                     dict.get('SecondFactorProvider', None),
                                     locations_parsed
                                     )

class AuthenticationTokenType(object):
    """Enumeration describing the kind of second factor that was used during a 2-step verification process during authentication"""

    NONE = 0
    SOFT = 1
    HARD = 2

class RefreshState(object):
    """Enumeration describing the current state of a financial refresh request for a miiCard user"""

    UNKNOWN = 0
    DATA_AVAILABLE = 1
    IN_PROGRESS = 2

class MiiFinancialData(object):
    """
    Represents a collection of financial data that a miiCard member has elected to share with a
    relying party.
    """

    def __init__(
                 self,
                 financial_providers
                 ):

        self.financial_providers = financial_providers

    @staticmethod
    def FromDict(dict):
        """Builds and returns a MiiFinancialData object from a dictionary of parameters"""

        financial_providers = dict.get('FinancialProviders', None)

        if financial_providers:
            financial_providers_parsed = []
            for financial_provider in financial_providers:
                financial_providers_parsed.append(FinancialProvider.FromDict(financial_provider))
        else:
            financial_providers_parsed = None

        return MiiFinancialData(
                                financial_providers_parsed
                                )

class FinancialProvider(object):
    """A single financial provider containing summary or transaction-level data."""

    def __init__(
                 self,
                 provider_name,
                 financial_accounts
                 ):

        self.provider_name = provider_name
        self.financial_accounts = financial_accounts

    @staticmethod
    def FromDict(dict):
        """Builds and returns a FinancialProvider object from a dictionary of parameters"""

        financial_accounts = dict.get('FinancialAccounts', None)

        if financial_accounts:
            financial_accounts_parsed = []
            for financial_account in financial_accounts:
                financial_accounts_parsed.append(FinancialAccount.FromDict(financial_account))
        else:
            financial_accounts_parsed = None

        return FinancialProvider(
                                 dict.get('ProviderName'),
                                 financial_accounts_parsed
                                 )

class FinancialAccount(object):
    """
    Details of a single financial account that a miiCard member has elected to share with a
    relying party application.
    """

    def __init__(
                 self,
                 account_name,
                 holder,
                 sort_code,
                 account_number,
                 type,
                 from_date,
                 last_updated_utc,
                 closing_balance,
                 debits_sum,
                 debits_count,
                 credits_sum,
                 credits_count,
                 currency_iso,
                 transactions
                 ):

        self.account_name = account_name
        self.holder = holder
        self.sort_code = sort_code
        self.account_number = account_number
        self.type = type
        self.from_date = from_date
        self.last_updated_utc = last_updated_utc
        self.closing_balance = closing_balance
        self.debits_sum = debits_sum
        self.debits_count = debits_count
        self.credits_sum = credits_sum
        self.credits_count = credits_count
        self.currency_iso = currency_iso
        self.transactions = transactions

    @staticmethod
    def FromDict(dict):
        """Builds and returns a FinancialAccount object from a dictionary of parameters"""

        transactions = dict.get('Transactions', None)

        if transactions:
            transactions_parsed = []
            for transaction in transactions:
                transactions_parsed.append(FinancialTransaction.FromDict(transaction))
        else:
            transactions_parsed = None

        return FinancialAccount(
                                dict.get('AccountName'),
                                dict.get('Holder'),
                                dict.get('SortCode'),
                                dict.get('AccountNumber'),
                                dict.get('Type'),
                                Util.try_parse_datetime_from_json_string(dict.get('FromDate', None)),
                                Util.try_parse_datetime_from_json_string(dict.get('LastUpdatedUtc', None)),
                                dict.get('ClosingBalance'),
                                dict.get('DebitsSum'),
                                dict.get('DebitsCount'),
                                dict.get('CreditsSum'),
                                dict.get('CreditsCount'),
                                dict.get('CurrencyIso'),
                                transactions_parsed
                                )

class FinancialTransaction(object):
    """A single transaction reported against a financial account whose details have been shared by a miiCard member."""

    def __init__(
                 self,
                 date,
                 amount_credited,
                 amount_debited,
                 description,
                 id
                 ):

        self.date = date
        self.amount_credited = amount_credited
        self.amount_debited = amount_debited
        self.description = description
        self.id = id

    @staticmethod
    def FromDict(dict):
        """Builds and returns a FinancialTransaction object from a dictionary of parameters"""

        return FinancialTransaction(
                                    Util.try_parse_datetime_from_json_string(dict.get('Date')),
                                    dict.get('AmountCredited', None),
                                    dict.get('AmountDebited', None),
                                    dict.get('Description'),
                                    dict.get('ID')
                                    )

class GeographicLocation(object):
    """Represents a miiCard member's geographic location as reported by a single data provider"""

    def __init__(
                 self,
                 location_provider,
                 latitude,
                 longitude,
                 lat_long_accuracy_metres,
                 approximate_address
                 ):

        self.location_provider = location_provider
        self.latitude = latitude
        self.longitude = longitude
        self.lat_long_accuracy_metres = lat_long_accuracy_metres
        self.approximate_address = approximate_address

    @staticmethod
    def FromDict(dict):
        """Builds and returns a GeographicLocation object from a dictionary of parameters"""

        return GeographicLocation(
                                  dict.get('LocationProvider', None),
                                  dict.get('Latitude', None),
                                  dict.get('Longitude', None),
                                  dict.get('LatLongAccuracyMetres', None),
                                  PostalAddress.FromDict(dict.get('ApproximateAddress', None))
                                  )

class MiiApiCallStatus(object):
    """Enumeration describing the overall status of an API call"""

    SUCCESS = 0
    FAILURE = 1

class MiiApiErrorCode(object):
    """Enumeration describing the specific problem that occurred when accessing the API, if any"""

    SUCCESS = 0
    ACCESS_REVOKED = 100,
    USER_SUBSCRIPTION_LAPSED = 200,
    TRANSACTIONAL_SUPPORT_DISABLED = 1000,
    DEVELOPMENT_TRANSACTIONAL_SUPPORT_ONLY = 1010,
    INVALID_SNAPSHOT_ID = 1020,
    BLACKLISTED = 2000,
    PRODUCT_DISABLED = 2010,
    PRODUCT_DELETED = 2020,
    EXCEPTION = 10000

class MiiApiResponse(object):
    """
    A wrapper around responses from API calls detailing success or failure of the call and
    the payload of the response itself
    """

    def __init__(self, status, error_code, error_message, is_test_user, data):
        self.status = status
        self.error_code = error_code
        self.error_message = error_message
        self.is_test_user = is_test_user
        self.data = data

    @staticmethod
    def FromDict(dict, data_processor, is_array_payload = False):
        """
        Builds and returns a MiiApiResponse object from a dictionary of parameters, parsing the parameters into a Python
        object using the data_processor callback if one is supplied
        """

        payload_json = dict.get('Data')

        if payload_json and data_processor:
            if is_array_payload:
                payload = []
                for payload_entry in payload_json:
                    payload.append(data_processor(payload_entry))
            else:
                payload = data_processor(payload_json)
        elif payload_json is not None:
            payload = payload_json
        else:
            payload = None

        return MiiApiResponse(
                              dict.get('Status', MiiApiCallStatus.SUCCESS),
                              dict.get('ErrorCode', MiiApiErrorCode.SUCCESS),
                              dict.get('ErrorMessage', None),
                              dict.get('IsTestUser', False),
                              payload
                              )

class IdentitySnapshotDetails(object):
    """
    Represents details about a single identity snapshot - a point-in-time representation of a miiCard
    member's identity information.
    """

    def __init__(self, snapshot_id, username, timestamp_utc, was_test_user):
        self.snapshot_id = snapshot_id
        self.username = username
        self.timestamp_utc = timestamp_utc
        self.was_test_user = was_test_user

    @staticmethod
    def FromDict(dict):
        """
        Builds and returns an IdentitySnapshotDetails object from a dictionary of parameters
        """

        return IdentitySnapshotDetails(
                                       dict.get('SnapshotId', None),
                                       dict.get('Username', None),
                                       Util.try_parse_datetime_from_json_string(dict.get('TimestampUtc', None)),
                                       dict.get('WasTestUser', False)
                                       )

class IdentitySnapshot(object):
    """
    Represents a point-in-time snapshot of a miiCard member's identity
    """

    def __init__(self, details, snapshot):
        self.details = details
        self.snapshot = snapshot

    @staticmethod
    def FromDict(dict):
        """
        Builds and returns an IdentitySnapshot object from a dictionary of parameters
        """
        return IdentitySnapshot(
                                IdentitySnapshotDetails.FromDict(dict.get('Details')),
                                MiiUserProfile.FromDict(dict.get('Snapshot'))
                               )

class MiiCardOAuthServiceBase(object):
    """Base class of OAuth wrappers around miiCard APIs"""

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        if consumer_key is None or consumer_secret is None or access_token is None or access_token_secret is None:
            raise ValueError
        
        self.consumer_key = consumer_key;
        self.consumer_secret = consumer_secret;
        self.access_token = access_token;
        self.access_token_secret = access_token_secret;

    def _make_request(self, url, post_data, payload_processor, wrapped_response = True, array_type_payload = False):
        # http://parand.com/say/index.php/2010/06/13/using-python-oauth2-to-access-oauth-protected-resources/
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        access_token = oauth.Token(self.access_token, self.access_token_secret)

        import httplib2
        httplib2.debuglevel = 1000

        client = OAuthClient(consumer, access_token)
        client.set_signature_method(oauth.SignatureMethod_HMAC_SHA1())

        new_headers = {'Content-Type': 'application/json'}
        if not post_data:
            new_headers['Content-Length'] = '0';

        response, content = client.request(url, method="POST", body=post_data, headers=new_headers)

        if wrapped_response:
            return MiiApiResponse.FromDict(json.loads(content), payload_processor, array_type_payload)
        elif payload_processor:
            return payload_processor(content)
        else:
            return content

class MiiCardOAuthClaimsService(MiiCardOAuthServiceBase):
    """Wrapper around the miiCard Claims API v1"""    

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        super(MiiCardOAuthClaimsService, self).__init__(consumer_key, consumer_secret, access_token, access_token_secret)

    def get_claims(self):
        """
        Returns a subset of the miiCard user's identity as agreed by the user, as a MiiApiResponse object whose data field
        is populated with a MiiUserProfile object
        """

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetClaims'),
                                  None,
                                  MiiUserProfile.FromDict
                                  )

    def is_social_account_assured(self, social_account_id, social_account_type):
        """
        Returns whether the miiCard user has verified ownership of a particular social network account as a MiiApiResponse
        object whose data field is populated with a boolean
        """

        post_params = json.dumps({"socialAccountId": social_account_id, "socialAccountType": social_account_type})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('IsSocialAccountAssured'),
                                  post_params,
                                  None
                                  )

    def is_user_assured(self):
        """
        Returns whether the miiCard user's identity has been assured to the level of assurance required by your developer profile 
        as a MiiApiResponse object whose data field is populated with a boolean
        """

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('IsUserAssured'),
                                  None,
                                  None
                                  )
    
    def assurance_image(self, type):
        """
        Returns an image representation of the identity assurance level of a user in a specified format, returning the
        PNG content of the image
        """

        post_params = json.dumps({"type": type})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('AssuranceImage'),
                                  post_params,
                                  None,
                                  wrapped_response = False
                                  )

    def get_card_image(self, snapshot_id = None, show_email_address = False, show_phone_number = False, format = None):
        """
        Returns a card-image representation of the miiCard member's identity assurance status, pulling that data from
        a snapshot specified by its ID (if supplied) or live data otherwise.
        """

        post_params = json.dumps({"SnapshotId": snapshot_id, "ShowEmailAddress": show_email_address, "ShowPhoneNumber": show_phone_number, "Format": format})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetCardImage'),
                                  post_params,
                                  None,
                                  wrapped_response = False
                                  )

    def get_identity_snapshot_details(self, snapshot_id = None):
        """
        Gets details of a snapshot identified by its ID, or of all snapshots for the miiCard member if
        not supplied.
        """

        post_params = json.dumps({"snapshotId": snapshot_id})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetIdentitySnapshotDetails'),
                                  post_params,
                                  IdentitySnapshotDetails.FromDict,
                                  array_type_payload = True
                                  )

    def get_identity_snapshot(self, snapshot_id):
        """
        Gets the snapshot of a miiCard member's identity specified by the supplied snapshot ID. To discover existing snapshots, 
        use the get_identity_snapshot_details function supplying no parameters.
        """

        post_params = json.dumps({"snapshotId": snapshot_id})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetIdentitySnapshot'),
                                  post_params,
                                  IdentitySnapshot.FromDict
                                  )
                              
    def get_identity_snapshot_pdf(self, snapshot_id):
        """
        Returns a PDF representation of an identity snapshot specified by its snapshot ID, as a byte stream.
        """

        post_params = json.dumps({"snapshotId": snapshot_id})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetIdentitySnapshotPdf'),
                                  post_params,
                                  None,
                                  wrapped_response = False
                                  )

    def get_authentication_details(self, snapshot_id):
        """
        Returns the authentication details of an identity snapshot by its snapshot ID, as an AuthenticationDetails object
        """

        post_params = json.dumps({"snapshotId": snapshot_id})

        return super(MiiCardOAuthClaimsService, self)._make_request(
                                  MiiCardServiceUrls.get_claims_method_url('GetAuthenticationDetails'),
                                  post_params,
                                  AuthenticationDetails.FromDict
                                  )

class MiiCardOAuthFinancialService(MiiCardOAuthServiceBase):
    """Wrapper around the miiCard Financial API v1"""

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        super(MiiCardOAuthFinancialService, self).__init__(consumer_key, consumer_secret, access_token, access_token_secret)

    def is_refresh_in_progress(self):
        """
        Returns whether the miiCard user's financial links are currently being refreshed by miiCard's data provider
        """

        return super(MiiCardOAuthFinancialService, self)._make_request(
                                  MiiCardServiceUrls.get_financial_method_url('IsRefreshInProgress'),
                                  None,
                                  None
                                  )

    def refresh_financial_data(self):
        """
        Makes a request to miiCard's data provider to refresh the financial links of a miiCard user, and returns the result
        """

        return super(MiiCardOAuthFinancialService, self)._make_request(
                                  MiiCardServiceUrls.get_financial_method_url('RefreshFinancialData'),
                                  None,
                                  FinancialRefreshStatus.FromDict
                                  )

    def get_financial_transactions(self):
        """
        Gets the transactions of a miiCard user's financial account(s)
        """

        return super(MiiCardOAuthFinancialService, self)._make_request(
                                  MiiCardServiceUrls.get_financial_method_url('GetFinancialTransactions'),
                                  None,
                                  MiiFinancialData.FromDict
                                  )

class MiiCardDirectoryService:
    CRITERION_USERNAME = "username"
    CRITERION_EMAIL = "email"
    CRITERION_PHONE = "phone"
    CRITERION_TWITTER = "twitter"
    CRITERION_FACEBOOK = "facebook"
    CRITERION_LINKEDIN = "linkedin"
    CRITERION_GOOGLE = "google"
    CRITERION_MICROSOFT_ID = "liveid"
    CRITERION_EBAY = "ebay"
    CRITERION_VERITAS_VITAE = "veritasvitae"

    def find_by_username(self, username, hashed = False):
        return find_by(CRITERION_USERNAME, username, hashed)

    def find_by_email(self, email, hashed = False):
        return find_by(CRITERION_EMAIL, email, hashed)

    def find_by_phone(phone, hashed = False):
        return find_by(CRITERION_PHONE, phone, hashed)

    def find_by_twitter(self, twitter_handle_or_profile_url, hashed = False):
        return find_by(CRITERION_TWITTER, twitter_handle_or_profile_url, hashed)

    def find_by_facebook(self, facebook_url, hashed = False):
        return find_by(CRITERION_FACEBOOK, facebook_url, hashed)

    def find_by_linkedin(self, linkedin_www_url, hashed = False):
        return find_by(CRITERION_LINKEDIN, linkedin_www_url, hashed)

    def find_by_google(self, google_handle_or_profile_url, hashed = False):
        return find_by(CRITERION_GOOGLE, google_handle_or_profile_url, hashed)

    def find_by_microsoft_id(self, microsoft_id_url, hashed = False):
        return find_by(CRITERION_MICROSOFT_ID, microsoft_id_url, hashed)

    def find_by_ebay(self, ebay_handle_or_profile_url, hashed = False):
        return find_by(CRITERION_EBAY, ebay_handle_or_profile_url, hashed)

    def find_by_veritas_vitae(self, veritas_vitae_vv_number_or_profile_url, hashed = False):
        return find_by(CRITERION_VERITAS_VITAE, veritas_vitae_vv_number_or_profile_url, hashed)

    def find_by(self, criterion, value, hashed = False):
        import httplib2
        http = httplib2.Http()

        url = MiiCardServiceUrls.get_directory_service_query_url(criterion, value, hashed)
        headers = {'Content-type': 'application/json'}

        response, content = http.request(url, 'GET', None, headers)

        toReturn = None
        if content is not None:
            parsed_content = MiiApiResponse.FromDict(json.loads(content), MiiUserProfile.FromDict)
            if parsed_content is not None:
                toReturn = parsed_content.data

        return toReturn

    def hash_identifier(self, identifier):
        return hashlib.sha1(identifier).hexdigest()

# Fixup for simplegeo OAuth bug
class OAuthClient(oauth.Client):
    def request(self, uri, method="GET", body='', headers=None,
        redirections=httplib2.DEFAULT_MAX_REDIRECTS, connection_type=None):
        DEFAULT_POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'

        if not isinstance(headers, dict):
            headers = {}

        if method == "POST" and 'Content-Type' not in headers:
            headers['Content-Type'] = headers.get('Content-Type',
                DEFAULT_POST_CONTENT_TYPE)

        is_form_encoded = \
            headers.get('Content-Type') == 'application/x-www-form-urlencoded'

        if is_form_encoded and body:
            parameters = parse_qs(body)
        else:
            parameters = None

        req = OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=method, http_url=uri,
            parameters=parameters, body=body, is_form_encoded=is_form_encoded)

        req.sign_request(self.method, self.consumer, self.token)

        schema, rest = urllib.splittype(uri)
        if rest.startswith('//'):
            hierpart = '//'
        else:
            hierpart = ''
        host, rest = urllib.splithost(rest)

        realm = schema + ':' + hierpart + host

        if is_form_encoded:
            body = req.to_postdata()
        elif method == "GET":
            uri = req.to_url()
        else:
            headers.update(req.to_header(realm=realm))

        ctx = httplib2.Http

        return ctx.request(self, uri, method=method, body=body,
            headers=headers, redirections=redirections,
            connection_type=connection_type)

class OAuthRequest(oauth.Request):
    def sign_request(self, signature_method, consumer, token):
        """Set the signature parameter to the result of sign."""

        if 'oauth_consumer_key' not in self:
            self['oauth_consumer_key'] = consumer.key

        if token and 'oauth_token' not in self:
            self['oauth_token'] = token.key

        self['oauth_signature_method'] = signature_method.name
        self['oauth_signature'] = signature_method.sign(self, consumer, token)

    @classmethod
    def from_consumer_and_token(cls, consumer, token=None,
            http_method=oauth.HTTP_METHOD, http_url=None, parameters=None,
            body='', is_form_encoded=False):
        if not parameters:
            parameters = {}
 
        defaults = {
            'oauth_consumer_key': consumer.key,
            'oauth_timestamp': cls.make_timestamp(),
            'oauth_nonce': cls.make_nonce(),
            'oauth_version': cls.version,
        }
 
        defaults.update(parameters)
        parameters = defaults
 
        if token:
            parameters['oauth_token'] = token.key
            if token.verifier:
                parameters['oauth_verifier'] = token.verifier
 
        return OAuthRequest(http_method, http_url, parameters, body=body,
                       is_form_encoded=is_form_encoded)

class Util(object):
    @staticmethod
    def try_parse_datetime_from_json_string(json_string):
        try:
            parsed = datetime.fromtimestamp(float(json_string[6:-2])/1000)
            return parsed
        except (ValueError, TypeError):
            return None
