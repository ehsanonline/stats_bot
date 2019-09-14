## Telegram Stats Bot
This is a simple python telegram bot that saves group users stats such as count of their text messages, stickers, voices and... into a redis database and send them via `/stats` command. just for fun and as a sample project!

### Featurers
Support count of these message types:
* texts
* stickers
* audios
* animations
* documents
* games
* photos
* videos
* voices
* video notes
* contacts
* locations
* venues
* polls
* count of new users that user adds
* user leaves group chat
* pinned messages by user

Total number of messages and last time that user send any type will be saved separately too.

### Commands
* any user can recevie his/her stats by sending `/stats` command in group.
* admins can receive stats of any user by replying a message of that user and send `/stats` command.
* to clear a user stats, admins can reply a message of that user and send `/clear` command.