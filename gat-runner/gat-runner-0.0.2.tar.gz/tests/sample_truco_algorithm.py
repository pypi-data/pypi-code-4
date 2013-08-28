import os
import socket
import sys
sys.path.append(os.getcwd())

from functools import update_wrapper

import gat_games.game_engine.gat_json as json

print('\n')
print('Running Sample Truco Algorithm')

# http://docs.python.org/2/library/argparse.html
# http://lucumr.pocoo.org/2012/6/26/disconnects-are-good-for-you/
port = int(sys.argv[1]) if len(sys.argv) > 1 else 58888
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Binding %s' % str(('localhost', port)))
sock.bind(('localhost', port))
print('Listening')
sock.listen(1)
conn, addr = sock.accept()
print('Client connected.')

def send_message(message):
    if sys.version_info[0] == 2:
        conn.sendall(message)
    else:
        conn.sendall(bytes(message, 'utf-8'))

while True:
    try:
        # print('\nWaiting for request')
        message = conn.recv(8192) # 2**13
        if not message or message == 'stop':
            break
        # print('\nRequest received: %s' % json.loads(message))
        message = json.loads(message)

        # print('Context %s' % message['context'])

        response = {'action': 'upcard', 'hand_card': message['context']['hand']['cards'][0]}

        # print('\nAnswer: %s' % response)
        response = json.dumps(response) + '\n'
        send_message(response)
        # print('\nSent' % response)
    except Exception as e:
        response = json.dumps({'error': str(e)})
        send_message(response)

conn.close()
