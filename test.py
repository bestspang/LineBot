import configparser, numpy

config = configparser.ConfigParser()
config.read("config.ini")

print(config['line_bot']['line_bot_api'])
print(config['line_bot']['handler'])
