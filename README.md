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
* add users
* leaves group chat
* pinned messages

Last time that user send any type will be saved too.

Admins can receive stats of any user by replying a message of that user and send `/stats` command.