import requests, time, sys, threading, re, sympy, importlib
from os.path import isfile, expanduser

# Gets config file from command
cFile = 'bot.cfg'
if len(sys.argv) == 2:
    cFile = sys.argv[1]
elif len(sys.argv) > 2:
    sys.exit('Unknown command sequence')
pyFile = 'default.py'

if isfile('./configs/' + cFile):
    cFile = './configs/' + cFile

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

# Import in the given response configuration
if isfile(pyFile):
    responses = importlib.import_module(pyFile.split('.')[0])
elif isfile('./configs/' + pyFile):
    responses = importlib.import_module('..' + pyFile.split('.')[0], 'configs.subpkg')
else:
    sys.exit('No response file found at ' + pyFile)

class Bot:
    # Sends a new message
    def sendMessage(self, text):
        post_params = { 'bot_id' : self.botId, 'text': text }
        requests.post('https://api.groupme.com/v3/bots/post', params=post_params)

    # Returns group info
    def getGroupItem(self, key):
        group_params = {'token': self.token}
        response = requests.get('https://api.groupme.com/v3/groups/' + self.group, params=group_params)
        if (response.status_code == 200):
            return response.json()['response'][key]

    # Shuts the bot down with a message
    def shutdown(self, msg, warn):
        self.run.clear()
        print(msg)
        if warn:
            print('Press enter to complete shutdown')

    # Fetches new messages every 3 seconds
    def fetchLoop(self, running):
        firstRun = True
        firstMsg = True
        request_params = {'token': self.token, 'limit': self.msgLimit}

        print('Listening for new messages...')
        while running.is_set():
            response = requests.get('https://api.groupme.com/v3/groups/' + self.group + '/messages', params=request_params)

            if (response.status_code == 200):
                response_messages = response.json()['response']['messages']

                # Loop through all new messages (since last ping)
                for message in response_messages:
                    # Get the newest id for fetching the next run
                    if firstMsg or request_params['since_id'] < message['id']:
                        request_params['since_id'] = message['id']
                        firstMsg = False

                    # Respond to new messages (ignore those arriving on startup)
                    if not firstRun and message['text'] != None:
                        print('[' + message['name'] + '] ' + message['text'])
                        threading.Thread(target=self.responses.processMessage, args=[message]).start()

                firstRun = False  

            time.sleep(3)

    # Locally send commands
    def inputLoop(self, running):
        print('Listening for local commands...')
        while running.is_set():
            cmdParts = input().split()
            if len(cmdParts) > 0:
                name = cmdParts[0]
                params = cmdParts[1:]
                found = False
                for cmd in self.cmds:
                    if name == cmd.name:
                        cmd.respond(params)
                        found = True
                if not found:
                    print('Invalid command!')

    # Listen for member changes every minute
    def memberLoop(self, running):
        print('Listening for member changes...')
        oldMems = self.getGroupItem('members')
        while running.is_set():
            mems = self.getGroupItem('members')
            if mems is not None:
                for m in mems:
                    for o in oldMems:
                        if m['user_id'] == o['user_id']:
                            self.responses.memberScan(m, o)
                            break
                oldMems = mems
            
            time.sleep(60)

    # Listen for updates every minute
    def updateLoop(self, running):
        print('Listening for updates...')
        while running.is_set():
            self.responses.update()
            time.sleep(60)

    def __init__(self, token, group, botId, msgLimit, responses):
        print('Starting Bot...')

        # Class Values
        self.token = token
        self.group = group
        self.botId = botId
        self.msgLimit = msgLimit
        self.responses = responses.BotResponses(self)

        # Initialize local commands
        self.cmds = []
        self.cmds.append(LocalCmd('send', '[message]', 'sends a message to the connected chat', self, lambda params: self.sendMessage(' '.join(params)) ))
        self.cmds.append(LocalCmd('shutdown', '', 'turns the bot off', self, lambda params: self.shutdown('Shutting down, this will take a moment...', False) ))
        self.cmds.append(LocalCmd('help', '', 'prints a list of commands', self, lambda params: [print(cmd.man()) for cmd in self.cmds] ))

        # Startup threads
        self.run = threading.Event()
        self.run.set()
        threading.Thread(target=self.fetchLoop, args=[self.run]).start()
        threading.Thread(target=self.inputLoop, args=[self.run]).start()
        threading.Thread(target=self.memberLoop, args=[self.run]).start()
        threading.Thread(target=self.updateLoop, args=[self.run]).start()

class LocalCmd():
    def __init__(self, name, options, description, bot, response):
        self.name = name
        self.ops = options
        self.desc = description
        self.bot = bot
        self.response = response
    
    def man(self):
        space = ''
        if self.ops:
            space = ' '
        return self.name + space + self.ops + ' - ' + self.desc

    def respond(self, params):
        self.response(params)

Bot(token, group, botId, 5, responses)