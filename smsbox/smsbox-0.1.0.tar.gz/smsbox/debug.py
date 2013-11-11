from commons import SMSBoxService


API_KEY = '{{ api key }}'
SIGNATURE = '{{ signature }}'
DEBUG = True
PHONE_NUMBER = '{{ phone number }}'
MESSAGE_TEXT = '{{ message text }}'

service = SMSBoxService(api_key=API_KEY, signature=SIGNATURE, debug=DEBUG)
print service.send_sms(phone_number=PHONE_NUMBER, message_text=MESSAGE_TEXT)
