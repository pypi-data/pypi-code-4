import requests
import datetime
import json


def get_payment_token(public_api_key,
                      card_number='4111111111111111',
                      expiration_month=None,
                      expiration_year=None,
                      verification_code='123'):
    """Get a payment token.

    Ported from the Java test suite.

    :param public_api_key: Public API key.
    :param card_number:
        Credit card number to use. Default ``4111 1111 1111 1111``.
    :param expiration_month:
        Credit card expiration month. Default ``None`` resulting in a valid
        expiration month being generated.
    :param expiration_year:
        Credit card expiration year. Default ``None`` resulting in a valid
        expiration year being generated.
    :param verification_code: Verification code. Default ``'123'``.
    :returns: a payment token.
    """

    # Perform the request.
    card_expiration = datetime.datetime.utcnow() + datetime.timedelta(days=45)
    response = requests.get(
        'https://test-token.paymill.de',
        verify=False,
        params={
            'channel.id': public_api_key,
            'account.number': card_number,
            'account.expiry.month': expiration_month or '%02d' %
            (card_expiration.month),
            'account.expiry.year': expiration_year or card_expiration.year,
            'account.verification': verification_code,
            'jsonPFunction': 'callback',
        }
    )

    response.raise_for_status()

    # Rid the horrible callback part and parse the JSON.
    json_raw = response.text[9:len(response.text) - 1]
    response_json = json.loads(json_raw)

    return response_json['transaction']['identification']['uniqueId']


def get_debit_payment_token(public_api_key,
                            holder='Max Mustermann',
                            country='DE',
                            bank_code='99999999',
                            account='1234567890',
                            amount=1000,
                            currency='EUR'):
    """Get a debit payment token.

    :param public_api_key: Public API key.
    :param holder: Account holder's name. Default ``Max Mustermann``.
    :param country:
        Account holder's country code in ISO 3166-alpha-2 format. Default
        ``DE``.
    :param bank_code: Bank code. Default ``99999999``.
    :param account: Account number. Default ``1234567890``.
    :param amount: Amount in hundredths of the currency. Default ``1000``.
    :param currency: Currency. Default ``EUR``.
    :returns: a payment token.
    """

    # Perform the request.
    response = requests.get(
        'https://test-token.paymill.de',
        verify=False,
        params={
            'channel.id': public_api_key,
            'account.bank': bank_code,
            'account.country': country,
            'account.holder': holder,
            'account.number': account,
            'jsonPFunction': 'callback',
        }
    )

    response.raise_for_status()

    # Rid the horrible callback part and parse the JSON.
    json_raw = response.text[9:len(response.text) - 1]
    response_json = json.loads(json_raw)

    return response_json['transaction']['identification']['uniqueId']
