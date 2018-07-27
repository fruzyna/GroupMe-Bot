import re
import sympy

class BotResponses:
    def __init__(self, bot):
        self.bot = bot

    # Parses a given message and crafts a response
    def processMessage(self, message):
        text = message['text'].lower()

        # Turn off the bot
        if 'shutdown' == text:
            self.bot.sendMessage('Shutting down...')
            self.bot.shutdown('Shut down by command', True)
            
        # Basic response
        if 'bot!' in text:
            self.bot.sendMessage('Hello there!')

        # Math calculations
        search = re.search('^calc\(([^a-zA-Z]+?)\)$', text)
        if search:
            self.bot.sendMessage('The answer is ' + str(sympy.sympify(search.group(1))))

    def memberScan(self, mem, oldMem):
        if mem['muted'] != oldMem['muted']:
            un = ''
            if mem['muted'] == False:
                un = 'un'
            self.bot.sendMessage(mem['nickname'] + ' is now ' + un + 'muted')