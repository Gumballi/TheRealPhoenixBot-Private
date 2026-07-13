# Simple dictionary module by @TheRealPhoenix (Updated)
import requests

from telegram import Bot, Message, Update, ParseMode
from telegram.ext import CommandHandler, run_async

from tg_bot import dispatcher


@run_async
def define(bot: Bot, update: Update, args):
    msg = update.effective_message
    if not args:
        msg.reply_text("Please provide a word to define! Example: /define python")
        return

    word = " ".join(args)
    # Using the active Free Dictionary API
    res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    
    if res.status_code == 200:
        try:
            # Extract meanings list from the first matched word entry
            meanings = res.json()[0].get("meanings")
            if meanings:
                meaning = ""
                for count, m in enumerate(meanings, start=1):
                    part_of_speech = m.get("partOfSpeech", "unknown")
                    meaning += f"<b>{count}. {word}</b> <i>({part_of_speech})</i>\n"
                    
                    # Loop through definitions for this specific part of speech
                    for i in m.get("definitions", []):
                        defs = i.get("definition")
                        meaning += f"• <i>{defs}</i>\n"
                
                msg.reply_text(meaning, parse_mode=ParseMode.HTML)
            else:
                msg.reply_text("No definitions found for that word.")
        except (IndexError, AttributeError, ValueError):
            msg.reply_text("Error parsing the dictionary results.")
    else:
        msg.reply_text("No results found!")


__help__ = """
Ever stumbled upon a word that you didn't know of and wanted to look it up?
With this module, you can find the definitions of words without having to leave the app!

*Available commands:*
 - /define <word>: returns the definition of the word.
 """
 
__mod_name__ = "Dictionary"


DEFINE_HANDLER = CommandHandler("define", define, pass_args=True)
dispatcher.add_handler(DEFINE_HANDLER)
