import hashlib
from copy import deepcopy
from django import forms
from django.forms import widgets
from django.utils.http import urlunquote
from buysafe.exceptions import ChecksumError
from buysafe.fields import NumberStringField, SunTechChecksumField
from buysafe.widgets import HiddenIntegerInput


###########
# Gadgets #
###########

def _sha1_hex_upper(*args):
    return hashlib.sha1(''.join([str(v) for v in args])).hexdigest().upper()


#################
# Generic forms #
#################

class SunTechForm(forms.Form):
    """
    A generic form for SunTech transactions. This class overrides `add_prefix`
    to perform a lookup to generate correct form field names for SunTech.
    Subclasses should override class attribute `FIELD_NAME_LOOKUP` to set up
    the lookup table.
    """
    FIELD_NAME_LOOKUP = {}

    def __init__(self, store_password, *args, **kwargs):
        super(SunTechForm, self).__init__(*args, **kwargs)
        self.store_password = store_password

    def add_prefix(self, field_name):
        # Look up field name; return original if not found
        field_name = self.FIELD_NAME_LOOKUP.get(
            field_name, field_name
        )
        return super(SunTechForm, self).add_prefix(field_name)


class SunTechSendForm(SunTechForm):
    """
    A generic form subclassing `SunTechForm` but transform all fields in it
    to be hidden. This class is abstract in concept and should be subclassed.
    """
    store_name = forms.CharField()
    price = forms.IntegerField()
    order_id = forms.IntegerField()
    order_info = forms.CharField(required=False)
    name = forms.CharField()
    phone = NumberStringField()
    email = forms.EmailField(required=False)
    note1 = forms.CharField(required=False)
    note2 = forms.CharField(required=False)
    checksum = SunTechChecksumField()

    FIELD_NAME_LOOKUP = {
        'store_name': 'web',
        'price': 'MN',
        'order_id': 'Td',
        'order_info': 'OrderInfo',
        'name': 'sna',
        'phone': 'sdt',
        'email': 'email',
        'note1': 'note1',
        'note2': 'note2',
        'checksum': 'ChkValue'
    }

    def __init__(self, *args, **kwargs):
        super(SunTechSendForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            field = self.fields[key]
            if isinstance(field, forms.IntegerField):
                field.widget = HiddenIntegerInput()
            else:
                field.widget = widgets.HiddenInput()

    def get_checksum(self):
        """
        Subclasses may override this method to provide another valid algorithm
        to generate and return a checksum from `self['field_name'].value()` and
        `self.store_password`. This is called by `fill_checksum`.
        """
        return _sha1_hex_upper(
            self['store_name'].value(),
            self.store_password,
            int(self['price'].value())
        )

    def fill_checksum(self, field_name='checksum'):
        """
        Fills the checksum field with get_checksum. The checksum field is named
        "checksum" by default, but you can pass in another name if needed.
        """
        self.fields[field_name].initial = self.get_checksum()


class SunTechReceiveForm(SunTechForm):
    """
    A generic form subclassing `SunTechForm` to provide `validate_checksum()`
    method. Subclasses should override this method to check for the form's
    checksum based on values in `self.cleaned_data` and `self.store_password`,
    raising a `ChecksumError` if the checksum is not correct.

    `validate_checksum` is called in `clean`. Therefore, all subclasses of
    `SunTechReceiveForm` should invoke `super` in their `clean` overrides.
    """
    sun_id = forms.CharField()
    store_name = forms.CharField()
    order_id = forms.IntegerField()
    price = forms.IntegerField()
    note1 = forms.CharField(required=False)
    note2 = forms.CharField(required=False)
    checksum = SunTechChecksumField()

    FIELD_NAME_LOOKUP = {
        'sun_id': 'buysafeno',
        'store_name': 'web',
        'order_id': 'Td',
        'price': 'MN',
        'note1': 'note1',
        'note2': 'note2',
        'checksum': 'ChkValue'
    }

    class SEND_TYPE:
        BACKGROUND = 1
        WEBPAGE = 2

    def validate_checksum(self, field_name='checksum'):
        reference = _sha1_hex_upper(
            self.cleaned_data['store_name'], self.store_password,
            self.cleaned_data['sun_id'], self.cleaned_data['price'],
            self.cleaned_data['return_code']
        )
        checksum = self.cleaned_data['checksum']
        if reference != checksum:
            raise ChecksumError(expected=reference, got=checksum)

    def clean(self):
        self.validate_checksum()
        return super(SunTechReceiveForm, self).clean()


SUNTECH_INSTANT_RESPONSE_LOOKUP = deepcopy(
    SunTechReceiveForm.FIELD_NAME_LOOKUP
)
SUNTECH_INSTANT_RESPONSE_LOOKUP.update({
    'name': 'Name',
    'site_name': 'webname',
    'send_type': 'SendType',
    'return_code': 'errcode',
    'return_detail': 'errmsg',
})


class SunTechInstantResponseForm(SunTechReceiveForm):
    """
    A generic form subclassing `SunTechReceiveForm` to be base of receive forms
    for payment methods with an "Instant Response," i.e. gets a response almost
    instantly because customer pays directly on the Internet.
    """
    name = forms.CharField()
    site_name = forms.CharField()
    send_type = forms.IntegerField(
        min_value=SunTechReceiveForm.SEND_TYPE.BACKGROUND,
        max_value=SunTechReceiveForm.SEND_TYPE.WEBPAGE
    )
    return_code = forms.CharField()
    return_detail = forms.CharField(required=False)

    FIELD_NAME_LOOKUP = SUNTECH_INSTANT_RESPONSE_LOOKUP

    def clean_name(self):
        name = urlunquote(self.cleaned_data['name'])
        return name

    def clean_site_name(self):
        site_name = urlunquote(self.cleaned_data['site_name'])
        return site_name

    def clean_return_detail(self):
        detail = urlunquote(self.cleaned_data['return_detail'])
        return detail

    def is_successful(self):
        return (self.cleaned_data.get('return_code') == '00')


SUNTECH_PAY_LATER_SEND_LOOKUP = deepcopy(SunTechSendForm.FIELD_NAME_LOOKUP)
SUNTECH_PAY_LATER_SEND_LOOKUP.update({
    'due_date': 'DueDate',
    'bill_date': 'BillDate',
    'user_id': 'UserNo'
})


class SunTechPayLaterSendForm(SunTechSendForm):
    """
    A generic form subclassing `SunTechSendForm` to be base of send forms for
    payment methods without an instant response. This kind of pyments usually
    consists a manual payment collection, such as offline ATM transactions.
    """
    due_date = forms.DateField(input_formats=["%Y%m%d"])
    bill_date = forms.DateField(input_formats=["%Y%m%d"])
    user_id = forms.IntegerField()

    FIELD_NAME_LOOKUP = SUNTECH_PAY_LATER_SEND_LOOKUP


SUNTECH_PAY_LATER_RECEIVE_LOOKUP = deepcopy(
    SunTechReceiveForm.FIELD_NAME_LOOKUP
)
SUNTECH_PAY_LATER_RECEIVE_LOOKUP.update({
    'return_code': 'errcode',
    'user_id': 'UserNo',
    'payment_date': 'PayDate',
    'payment_type': 'PayType'
})


class SunTechPayLaterReceiveForm(SunTechReceiveForm):
    """
    A generic form subclassing `SunTechReceiveForm` to be base of receive forms
    for payment methods without an instant response. This kind of pyments
    usually consists a manual payment collection, such as offline ATM
    transactions.
    """
    class PAYMENT_TYPE:
        BARCODE_CONVINIENCE_STORE = 1
        BARCODE_POST_OFFICE = 2
        VIRTUAL_ACCOUNT = 3
        CASH_CONVINIENCE_STORE = 4

    return_code = forms.CharField()
    user_id = forms.IntegerField()
    payment_date = forms.DateField(input_formats=["%Y%m%d"])
    payment_type = forms.IntegerField(
        min_value=PAYMENT_TYPE.BARCODE_CONVINIENCE_STORE,
        max_value=PAYMENT_TYPE.CASH_CONVINIENCE_STORE
    )

    FIELD_NAME_LOOKUP = SUNTECH_PAY_LATER_RECEIVE_LOOKUP


#################
# BuySafe forms #
#################

class BuySafeSendForm(SunTechSendForm):
    pass


BUYSAFE_RECEIVE_LOOKUP = deepcopy(SunTechInstantResponseForm.FIELD_NAME_LOOKUP)
BUYSAFE_RECEIVE_LOOKUP.update({
    'auth_code': 'ApproveCode',
    'card_number_tail': 'Card_NO',
})


class BuySafeReceiveForm(SunTechInstantResponseForm):
    auth_code = NumberStringField(required=False)
    card_number_tail = NumberStringField(max_length=4, required=False)

    FIELD_NAME_LOOKUP = BUYSAFE_RECEIVE_LOOKUP

    def clean(self):
        self.cleaned_data = super(BuySafeReceiveForm, self).clean()

        # Validate fields that are only available when return_code is 00
        if self.cleaned_data['return_code'] == '00':
            if not self.cleaned_data.get('auth_code', None):
                raise forms.ValidationError(
                    'Stated as successful, but auth code not presented.'
                )
            if len(self.cleaned_data.get('card_number_tail', '')) != 4:
                raise forms.ValidationError(
                    'Stated as successful, but credit card number not '
                    'presented.'
                )
        return self.cleaned_data


#################
# Web ATM forms #
#################

class WebATMSendForm(SunTechSendForm):
    pass


class WebATMReceiveForm(SunTechInstantResponseForm):
    pass


###############
# 24Pay forms #
###############

# class Pay24FormMeta(forms.DeclarativeFieldsMetaclass):
#     """
#     Metaclass to generate product name, price and quantity fields
#     """
#     def __new__(cls, name, bases, attrs):
#         for suffix, field_type in zip(
#                 ['name', 'price', 'quantity'],
#                 [forms.CharField, forms.DecimalField, forms.IntegerField]
#         ):
#             for i in range(10):
#                 name = '_'.join(['product', suffix, str(i)])
#                 attrs[name] = field_type(required=False)
#         return forms.DeclarativeFieldsMetaclass.__new__(
#             cls, name, bases, attrs
#         )


# PAY24_SEND_LOOKUP = deepcopy(SunTechPayLaterSendForm.FIELD_NAME_LOOKUP)
# for f, h in zip(['name', 'unit_price', 'quantity'],
#                 ['Name', 'Price', 'Quantity']):
#     for i in range(10):
#         fn = '_'.join(['product', f, str(i)])
#         hn = ''.join(['Product', h, str(i + 1)])
#         PAY24_SEND_LOOKUP[fn] = hn


# class Pay24SendForm(SunTechPayLaterSendForm):
#     product_count = 0

#     FIELD_NAME_LOOKUP = PAY24_SEND_LOOKUP

#     def add_product(self, product_name, )


# class Pay24ReceiveForm(SunTechPayLaterReceiveForm):
#     pass


#################
# PayCode forms #
#################

class PayCodeSendForm(SunTechPayLaterSendForm):
    pass


PAY_CODE_INSTANT_LOOKUP = deepcopy(SunTechReceiveForm.FIELD_NAME_LOOKUP)
PAY_CODE_INSTANT_LOOKUP.update({
    'user_id': 'UserNo',
    'payment_id': 'paycode'
})


class PayCodeInstantReceiveForm(SunTechReceiveForm):
    user_id = forms.IntegerField()
    payment_id = forms.CharField()

    FIELD_NAME_LOOKUP = PAY_CODE_INSTANT_LOOKUP


class PayCodeReceiveForm(SunTechPayLaterReceiveForm):
    pass
