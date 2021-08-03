from bot import GiveawayBot

import json



def main():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    bot = GiveawayBot(config)
    bot.remove_command("help")
    bot.run()


if __name__ == "__main__":
    main()