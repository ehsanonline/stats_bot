from telegram.ext import Updater,MessageHandler,CallbackContext
from telegram import Update
from src.config import config


class Bot :
  def start(self):
    updater = Updater(config["token"], use_context=True)
    updater.dispatcher.add_handler(MessageHandler(None,callback=self.new_message))
    updater.start_polling()
    updater.idle()
  def new_message(self, update: Update, context: CallbackContext):
    pass
