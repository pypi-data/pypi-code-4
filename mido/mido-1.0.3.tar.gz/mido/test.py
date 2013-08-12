import mido

mido.set_backend('.rtmidi')
print(mido.open_input('test', virtual=True))

