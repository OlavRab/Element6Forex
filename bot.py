import telebot
import logging
import element6
import secrets
from datetime import date
from time import sleep

bot = telebot.TeleBot(secrets.TOKEN)


def check_hello_message(message) -> bool:
    if message.text in ('Hello', 'Hell', 'Hi', 'Hey'):
        return True
    else:
        return False

#Command for the first conversation with the bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Element 6 Forex Trading Bot. \nIn Order for you to be helped, we need to validate your username, do so by replying 'Hello' to this message!")


#Handle first time users, make sure they're registered in the subs table
@bot.message_handler(func=check_hello_message)
def register_user(message):
    username = message.from_user.username
    userid = message.from_user.id

    existinguser = element6.dbquery(f"SELECT CASE WHEN COUNT(*) >= 1 THEN True ELSE FALSE END AS IsSub FROM Subscribers WHERE TelegramID = {userid}")

    if existinguser:
        bot.reply_to(message, "It seems that you have already registered to this service, Activate Forex signalling with command /startsignals")
    else:
        element6.dbquery(f"INSERT INTO Subscribers VALUES (DEFAULT, {message.from_user.id}, 1, 1, {date.today()}, NULL)")
        bot.reply_to(message, "Completed your registration!")


@bot.message_handler(commands=['announce'])
def announce(message) -> None:
    userid = message.from_user.id
    print(userid)
    if privileged(userid=userid):
        try:
            msg = message.text[10:]
            bot.send_message(chat_id=userid, text=msg)
        except BaseException as e:
            logging.error(f"Exception while broadcasting message {e}")
            
        # subs = element6.dbquery("SELECT * FROM subscribers")

        # for sub in subs:
            # sleep(1/29)

    else:
        print("Not Authorized")


@bot.message_handler(commands=['startsignals'])
def startsignals(message) -> None: 
    if subscriber(message.from_user.id):
        bot.reply_to(message, "You will now receive signals for all forex pairs, use /Filter to change your preferences")
    else:
        bot.reply_to(message, "You do not have an active subscription")

@bot.message_handler(commands=['filter'])
def filter(message) -> None:
    bot.reply_to(message, "Current Forex Pairs:\n" + "\n".join(secrets.FOREXPAIRS))

def subscriber (userid: int) -> bool:
    subscriber = element6.dbquery(f"SELECT COUNT(*) FROM Subscribers WHERE TelegramID = {userid}")
    if subscriber is None or subscriber == 0:
        return False
    else:
        return True 

def privileged(userid: int, check_only: bool = True) -> bool:
    admins = element6.dbquery(query="SELECT DISTINCT TelegramID FROM Subscribers WHERE UserLevel = 10")
    admin_ids = [item[0] for item in admins]
    if userid in admin_ids:
        logging.info(f"Privilege Attempt Granted to {userid}")
        return True
    else:
        logging.warning(f"Unauthorized privilege attempt by ID {userid}.")
        return False

bot.infinity_polling()
