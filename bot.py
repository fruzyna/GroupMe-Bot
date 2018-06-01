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
    sys.exit('Unknown command sequence')
cFile = expanduser(cFile)

# Checks for and loads config file
if isfile(cFile):
    # Read from existing file
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
    # Create new template file
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

    # Turn off the bot
    if 'Screw off you mother loving bot!' == message['text']:
        sendMessage('Shutting down...')
        sys.exit('Shut down by command')
        
    # Basic response
    if 'bot!' in text:
        sendMessage('Hello there!')

    # Self explanatory
    if re.search('suck.*dick', text):
        sendMessage('I found one for you right here --> 8===D')

    # Math calculations, disabled letters for security, not perfect but better
    # TODO safer method of calculation
    search = re.search('^calc\(([^a-zA-Z]+?)\)$', text)
    if search:
        sendMessage('The answer is ' + str(eval(search.group(1))))

    # TODO send messages to external file for plugins

# Fetches new messages every 3 seconds
while True:
    response = requests.get('https://api.groupme.com/v3/groups/' + group + '/messages', params=request_params)

    if (response.status_code == 200):
        response_messages = response.json()['response']['messages']

        # Loop through all new messages (since last ping)
        for message in response_messages:
            # Get the newest id for fetching the next run
            if firstMsg or request_params['since_id'] < message['id']:
                request_params['since_id'] = message['id']

            # Respond to new messages (ignore those arriving on startup)
            if not firstRun and message['user_id'] != botId:
                print('[' + message['name'] + '] ' + message['text'])
                processMessage(message)

            firstMsg = False

        if firstRun:
            firstRun = False      

    time.sleep(3)