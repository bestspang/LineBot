import configparser

config = configparser.ConfigParser()
config.read("config.ini")

print(config['line_bot']['line_bot_api'])
