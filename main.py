import configparser
import logging
import sys

import telegram
from flask import Flask, request
from telegram import ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

from nlp.olami import Olami

config = configparser.ConfigParser()
config.read('config.ini')
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))
dispatcher = Dispatcher(bot, None)

welcome_message = '親愛的主人，您可以問我\n' \
                  '天氣，例如：「高雄天氣如何」\n' \
                  '百科，例如：「川普是誰」\n' \
                  '新聞，例如：「今日新聞」\n' \
                  '音樂，例如：「我想聽周杰倫的等你下課」\n' \
                  '日曆，例如：「現在時間」\n' \
                  '詩詞，例如：「我想聽水調歌頭這首詩」\n' \
                  '笑話，例如：「講個笑話」\n' \
                  '故事，例如：「說個故事」\n' \
                  '股票，例如：「台積電的股價」\n' \
                  '聊天，例如：「你好嗎」'
reply_keyboard_markup = ReplyKeyboardMarkup([['高雄天氣如何'],
                                             ['川普是誰'],
                                             ['今日新聞'],
                                             ['我想聽周杰倫的等你下課'],
                                             ['現在時間'],
                                             ['我想聽水調歌頭這首詩'],
                                             ['講個笑話'],
                                             ['說個故事'],
                                             ['台積電的股價'],
                                             ['你好嗎']])


def _set_webhook():
    status = bot.set_webhook(config['TELEGRAM']['WEBHOOK_URL'])
    if not status:
        print('Webhook setup failed')
        sys.exit(1)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return 'ok'


def start_handler(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(welcome_message, reply_markup=reply_keyboard_markup)


def help_handler(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(welcome_message, reply_markup=reply_keyboard_markup)


def reply_handler(bot, update):
    """Reply message."""
    text = update.message.text
    logger.error(text)
    reply = Olami().nli(text)
    update.message.reply_text(reply)


def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)
    update.message.reply_text('對不起主人，我需要多一點時間來處理 Q_Q')


if __name__ == "__main__":
    _set_webhook()
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
    dispatcher.add_error_handler(error_handler)
    app.run()
