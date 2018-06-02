# Parses a given message and crafts a response
def processMessage(message):
    text = message['text'].lower()

    # Turn off the bot
    if 'shutdown' == text:
        sendMessage('Shutting down...')
        shutdown('Shut down by command', True)
        
    # Basic response
    if 'bot!' in text:
        sendMessage('Hello there!')

    # Math calculations
    search = re.search('^calc\(([^a-zA-Z]+?)\)$', text)
    if search:
        sendMessage('The answer is ' + str(sympy.sympify(search.group(1))))