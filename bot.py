import requests
import time
import re
import sys
from os.path import isfile, expanduser

# Gets config file from command
cFile = 'bot.cfg'
if len(sys.argv) == 2:
    cFile = sys.argv[1]
elif len(sys.argv) > 2:
    exit('Unknown command sequence')
cFile = expanduser(cFile)

# Checks for and loads config file
if isfile(cFile):
    f = open(cFile, 'r')
    for l in f.read().split('\n'):
        parts = l.split('=')
        if parts[0] == 'token' and parts[1] != '[API KEY]':
            token = parts[1]
        elif parts[0] == 'group' and parts[1] != '[GROUP ID]':
            group = parts[1]
        elif parts[0] == 'botId' and parts[1] != '[BOT ID]':
            botId = parts[1]
else:
    f = open(cFile, 'w+')
    f.write('token=[API KEY]\n')
    f.write('group=[GROUP ID]\n')
    f.write('botId=[BOT ID]')
    f.close()
    sys.exit('No config file found at ' + cFile)

# Global variables
firstRun = True
firstMsg = True
request_params = {'token': token}

# Sends a new message
def sendMessage(text):
    post_params = { 'bot_id' : botId, 'text': text }
    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)

# Parses a given message and crafts a response
def processMessage(message):
    text = message['text'].lower()

    if 'Screw off you mother loving bot!' == message['text']:
        sendMessage('Shutting down...')
        sys.exit('Shut down by command')
        
    if 'bot!' in text:
        sendMessage('Hello there!')

    if 'suck a dick' in text:
        sendMessage('I found one for you right here --> 8===D')

    search = re.search('^calc\((.+?)\)$', text)
    if search:
        sendMessage('The answer is ' + str(eval(search.group(1))))
    else:
        return

# Fetches new messages ever 3 seconds
while True:
    response = requests.get('https://api.groupme.com/v3/groups/' + group + '/messages', params=request_params)

    if (response.status_code == 200):
        response_messages = response.json()['response']['messages']

        for message in response_messages:
            if firstMsg or request_params['since_id'] < message['id']:
                request_params['since_id'] = message['id']

            if not firstRun and message['user_id'] != botId:
                print('[' + message['name'] + '] ' + message['text'])
                processMessage(message)

            firstMsg = False

        if firstRun:
            firstRun = False      

    time.sleep(3)