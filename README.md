# GroupMe Bot Framework
This framework allows a user to easily create GroupMe bots my making a configuration file for each bot then optionally writing a small script to add responses. The default responses and examples are provided in default.py. It is intented to be extended for future bots. All configuration files should be placed either in the root directory of this repo or the ./configs directory. The framework looks for these file in each directory so a path before the file in not needed.

### Config File
A config file contains the basic information for connecting the bot to the GroupMe api. Values are saved in the [key]=[value] format. Below is a list of keys:
- token: your GroupMe developer token
- group: id number of the GroupMe group
- botId: id of the bot created
- exFun: response file to load from (not provided defaults to default.py)
All of the above information can be obtained from [dev.groupme.com](https://dev.groupme.com/)

### Execution
If the user desired to use bot.cfg and default.py for execution only `python bot.py` needs to be run. Otherwise, the call is `python bot.py [config.cfg]`.