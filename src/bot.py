import time

import redis
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Updater

from src.config import config

try:
  r = redis.Redis(host=config['redis-server'], port=config['redis-port'],
                  db=config['redis-db-number'], charset="utf-8", decode_responses=True)
except Exception as e:
  print("Error while connecting to database, ", str(e))
  exit()

types = [
    'text',
    'sticker',
    'audio',
    'animation',
    'document',
    'game',
    'photo',
    'video',
    'voice',
    'video_note',
    'contact',
    'location',
    'venue',
    'poll',
    'new_chat_members',
    'left_chat_member',
    'pinned_message']


class Bot:
  def start(self):
    updater = Updater(config["token"], use_context=True)
    updater.dispatcher.add_handler(
        MessageHandler(None, callback=self.new_message))
    updater.dispatcher.add_error_handler(self.error_cb)
    updater.start_polling()
    updater.idle()

  def error_cb(self, update: Update, context: CallbackContext):
    print(context.error)

  def new_message(self, update: Update, context: CallbackContext):
    if not update.message or not update.message.from_user or not update.message.chat or update.message.chat.type not in ['supergroup', 'group']:
      return
    name = 'chat:{}_user:{}'.format(
        update.message.chat.id, update.message.from_user.id)
    data = r.hgetall(name)
    for i in types:
      if hasattr(update.message, i) and getattr(update.message, i):
        data[i] = int(data[i])+1 if i in data and data[i] else 1
        data['last_'+i] = time.time()
        break
    data['total'] = int(data['total'])+1 if 'total' in data and data['total'] else 1
    data['last_message'] = time.time()
    r.hmset(name, data)
