# Urban Dictionary module by @TheRealPhoenix (Updated)
import re
import requests

from telegram import Bot, Message, Update, ParseMode
from telegram.ext import CommandHandler, run_async

from tg_bot import dispatcher


def clean_bracketed_text(text: str) -> str:
    """Removes the brackets around linked terms (e.g., [bruh] -> bruh)"""
    if not text:
        return ""
    return re.sub(r'\[(.*?)\]', r'\1', text)


@run_async
def urban(bot: Bot, update: Update, args):
    msg = update.effective_message
    if not args:
        msg.reply_text("Please provide a slang/word to search! Example: /urban flex")
        return

    word = " ".join(args)
    # Fetching directly from the official Urban Dictionary API
    res = requests.get(f"https://api.urbandictionary.com/v0/define?term={word}")
    
    if res.status_code == 200:
        data = res.json()
        results = data.get("list", [])
        
        if not results:
            msg.reply_text(f"Could not find any results for '{word}' on Urban Dictionary!")
            return
            
        # Get the top voted definition
        top_def = results[0]
        definition = clean_bracketed_text(top_def.get("definition", "No definition available."))
        example = clean_bracketed_text(top_def.get("example", ""))
        
        # Format votes
        thumbs_up = top_def.get("thumbs_up", 0)
        thumbs_down = top_def.get("thumbs_down", 0)
        
        # Build the response message
        reply = f"<b>Word:</b> {word.title()}\n\n"
        reply += f"<b>Definition:</b>\n<i>{definition}</i>\n\n"
        
        if example:
            reply += f"<b>Example:</b>\n<i>{example}</i>\n\n"
            
        reply += f"👍 {thumbs_up} | 👎 {thumbs_down}"
        
        msg.reply_text(reply, parse_mode=ParseMode.HTML)
    else:
        msg.reply_text("Failed to connect to Urban Dictionary. Try again later!")


__help__ = """
Look up the latest internet slang, memes, and cultural terms directly from Urban Dictionary!

*Available commands:*
 - /urban <word/phrase>: returns the top definition and example.
 """
 
__mod_name__ = "Urban Dictionary"


URBAN_HANDLER = CommandHandler("urban", urban, pass_args=True)
dispatcher.add_handler(URBAN_HANDLER)
