import keyring
import getpass


pw = getpass.getpass()

keyring.set_password('twilio', 'AC00c9739a1539392c4a97f5dc3f5d94c2', pw)
