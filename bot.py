import requests, time, sys, threading, re, sympy
from os.path import isfile, expanduser

# Gets config file from command
cFile = 'bot.cfg'
if len(sys.argv) == 2:
    cFile = sys.argv[1]
elif len(sys.argv) > 2:
    sys.exit('Unknown command sequence')
cFile = expanduser(cFile)

pyFile = 'default.py'

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
        elif parts[0] == 'exFun' and parts[1] != '[External Python Function]':
            pyFile = parts[1]
else:
    # Create new template file
    f = open(cFile, 'w+')
    f.write('token=[API KEY]\ngroup=[GROUP ID]\nbotId=[BOT ID]\nexFun=bot.py')
    f.close()
    sys.exit('No config file found at ' + cFile)

# Load in the response configuration
pyFile = expanduser(pyFile)
if isfile(pyFile):
    pyFileTxt = open(pyFile, 'r').read()
    exec(pyFileTxt)
else:
    sys.exit('No response file found at ' + pyFile)

msgLimit = 5
request_params = {'token': token, 'limit': msgLimit}

# Sends a new message
def sendMessage(text):
    post_params = { 'bot_id' : botId, 'text': text }
    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)

# Shuts the bot down with a message
def shutdown(msg, warn):
    run.clear()
    if warn:
        print('Press enter to complete shutdown')

# Fetches new messages every 3 seconds
def fetchLoop(running):
    firstRun = True
    firstMsg = True

    while running.is_set():
        response = requests.get('https://api.groupme.com/v3/groups/' + group + '/messages', params=request_params)

        if (response.status_code == 200):
            response_messages = response.json()['response']['messages']

            # Loop through all new messages (since last ping)
            for message in response_messages:
                # Get the newest id for fetching the next run
                if firstMsg or request_params['since_id'] < message['id']:
                    request_params['since_id'] = message['id']

                # Respond to new messages (ignore those arriving on startup)
                if not firstRun and message['text'] != None:
                    print('[' + message['name'] + '] ' + message['text'])
                    threading.Thread(target=processMessage, args=[message]).start()

                firstMsg = False

            if firstRun:
                firstRun = False  

        time.sleep(3)

# Locally send commands
def inputLoop(running):
    while running.is_set():
        cmdParts = input().split()
        if len(cmdParts) > 0:
            cmd = cmdParts[0]
            if cmd == 'send':
                sendMessage(' '.join(cmdParts[1:]))
            elif cmd == 'shutdown':
                shutdown('Shutting down', False)

# Startup threads
run = threading.Event()
run.set()
threading.Thread(target=fetchLoop, args=[run]).start()
threading.Thread(target=inputLoop, args=[run]).start()