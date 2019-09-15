import datetime
import time

import redis
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, MessageHandler,
                          Updater)

from src.config import config

try:
  r = redis.Redis(host=config['redis-server'], port=config['redis-port'],
                  db=config['redis-db-number'], charset="utf-8", decode_responses=True)
except Exception as e:
  print("Error while connecting to database, ", str(e))
  exit()

types = {
    'text': ['📝', 'Text', 'Texts'],
    'sticker': ['🧩', 'Sticker', 'Stickers'],
    'audio': ['🎶', 'Music', 'Music'],
    'animation': ['🎭', 'Animation', 'Animations'],
    'document': ['🗄', 'Document', 'Ducuments'],
    'game': ['🎮', 'Game', 'Games'],
    'photo': ['🖼', 'Photo', 'Photos'],
    'video': ['🎬', 'Video', 'Videos'],
    'voice': ['🗣', 'Voice', 'Voices'],
    'video_note': ['🎦', 'Video Note', 'Video Notes'],
    'contact': ['👥', 'Contact', 'Contacts'],
    'location': ['📍', 'Location', 'Locations'],
    'venue': ['🗺', 'Venue', 'Venues'],
    'poll': ['📊', 'Poll', 'Polls'],
    'new_chat_members': ['👤', 'Join/Add Member', 'Joins/Add Members'],
    'left_chat_member': ['👣', 'Leave', 'Leaves'],
    'pinned_message': ['📌', 'Pin', 'Pins']
}


class Bot:
  me = None

  def start(self):
    updater = Updater(config["token"], use_context=True)
    updater.dispatcher.add_handler(
        CommandHandler('stats', callback=self.stats_command))
    updater.dispatcher.add_handler(
        CommandHandler('clear', callback=self.clear_command))
    updater.dispatcher.add_handler(
        MessageHandler(None, callback=self.new_message))

    updater.dispatcher.add_error_handler(self.error_cb)
    self.me = updater.bot.get_me()
    print(self.me.username, 'started.')
    updater.start_polling()
    updater.idle()

  def error_cb(self, update: Update, context: CallbackContext):
    print("Error: ", context.error)

  def new_message(self, update: Update, context: CallbackContext):
    if not update.message or not update.message.from_user or not update.message.chat or update.message.chat.type not in ['supergroup', 'group']:
      return
    name = 'chat:{}_user:{}'.format(
        update.message.chat.id, update.message.from_user.id)
    data = r.hgetall(name)
    for i in types.keys():
      if hasattr(update.message, i) and getattr(update.message, i):
        data[i] = int(data[i])+1 if i in data and data[i] else 1
        data['last_'+i] = time.time()
        break
    data['total'] = int(data['total']) + \
        1 if 'total' in data and data['total'] else 1
    data['last_message'] = time.time()
    r.hmset(name, data)

  def stats_command(self, update: Update, context: CallbackContext):
    if not update.message or not update.message.from_user or not update.message.chat or update.message.chat.type not in ['supergroup', 'group']:
      return
    if update.message.reply_to_message:
      if not self.is_admin(context.bot, update.message.chat.id, update.message.from_user.id):
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text='Sorry, only admins can receive other members stats. To see your own stats, send /stats without replying.',
            reply_to_message_id=update.message.message_id)
        return
      user = update.message.reply_to_message.from_user
    else:
      user = update.message.from_user
    name = 'chat:{}_user:{}'.format(update.message.chat.id, user.id)
    data = r.hgetall(name)
    out = '{} stats:\n'.format(self.get_inlined_name(user))
    t = types.keys()
    count = 0
    for k, v in data.items():
      if k in t:
        count += 1
        out += '{} {}: <b>{}</b> <i>last: {}</i>\n'.format(types[k][0], types[k][1 if v == '1' else 2], v, datetime.datetime.fromtimestamp(
            float(data['last_'+k])).strftime("%y/%d/%m %H:%M"))
    if not count:
      context.bot.send_message(
          chat_id=update.message.chat.id,
          text='{} has no stats yet.'.format(self.get_inlined_name(user)),
          parse_mode='html',
          reply_to_message_id=update.message.message_id)
      return
    out += '{}: <b>{}</b> <i>last: {}</i>'.format('Total', data['total'], datetime.datetime.fromtimestamp(
        float(data['last_message'])).strftime("%y/%d/%m %H:%M"))
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=out,
        parse_mode='html',
        reply_to_message_id=update.message.message_id)

  def clear_command(self, update: Update, context: CallbackContext):
    if not update.message or not update.message.from_user or not update.message.chat or update.message.chat.type not in ['supergroup', 'group']:
      return
    if not self.is_admin(context.bot, update.message.chat.id, update.message.from_user.id):
      context.bot.send_message(
          chat_id=update.message.chat.id,
          text='Sorry, only admins can clear members stats.',
          reply_to_message_id=update.message.message_id)
      return
    if update.message.reply_to_message:
      user = update.message.reply_to_message.from_user
    else:
      user = update.message.from_user
    name = 'chat:{}_user:{}'.format(update.message.chat.id, user.id)
    if r.delete(name):
      context.bot.send_message(
          chat_id=update.message.chat.id,
          text='{} stats cleared.'.format(self.get_inlined_name(user)),
          parse_mode='html',
          reply_to_message_id=update.message.message_id)

  def get_fullname(self, user):
    return user.first_name+(' '+user.last_name if user.last_name else '')

  def get_inlined_name(self, user):
    return '<a href="tg://user?id={}">{}</a>'.format(user.id, self.get_fullname(user))

  def is_admin(self, bot, chat_id, user_id):
    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status in ['creator', 'administrator']:
      return True
    return False
