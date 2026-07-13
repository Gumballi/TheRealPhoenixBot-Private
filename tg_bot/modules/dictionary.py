import requests
from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler, run_async
from tg_bot import dispatcher

@run_async
def define(bot: Bot, update: Update, args):
    msg = update.effective_message
    
    # Check if the user actually provided a word to search
    if not args:
        msg.reply_text("Please provide a word to define! Example: `/define apple`", parse_mode=ParseMode.MARKDOWN)
        return

    # clean the input word (lowercase and strip whitespace)
    word = args[0].strip().lower()
    
    # Show typing action to let the user know the bot is working
    bot.send_chat_action(chat_id=msg.chat_id, action="typing")
    
    try:
        # Request data from dictionaryapi.dev (with a solid 8-second timeout)
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=8)
        
        if res.status_code == 200:
            data = res.json()
            if not isinstance(data, list) or len(data) == 0:
                msg.reply_text(f"Could not parse a valid definition for '<b>{word}</b>'.", parse_mode=ParseMode.HTML)
                return
                
            first_entry = data[0]
            word_name = first_entry.get("word", word).title()
            
            # Start formatting the HTML response string
            reply = f"<b>Word:</b> {word_name}\n"
            
            # Grab phonetic spelling if it exists
            phonetic = first_entry.get("phonetic")
            if phonetic:
                reply += f"<i>{phonetic}</i>\n"
            
            reply += "\n"
            
            # Extract up to 3 meanings/definitions to keep the telegram message clean
            meanings = first_entry.get("meanings", [])
            if meanings:
                for index, meaning in enumerate(meanings[:3], 1):
                    part_of_speech = meaning.get("partOfSpeech", "noun").capitalize()
                    definitions = meaning.get("definitions", [])
                    
                    if definitions:
                        definition_text = definitions[0].get("definition", "No definition text found.")
                        example_text = definitions[0].get("example", "")
                        
                        reply += f"<b>{index}. [{part_of_speech}]</b>\n"
                        reply += f"<i>{definition_text}</i>\n"
                        
                        if example_text:
                            reply += f"\"{example_text}\"\n"
                        reply += "\n"
                
                # Strip trailing clean whitespace before sending
                msg.reply_text(reply.strip(), parse_mode=ParseMode.HTML)
            else:
                msg.reply_text(f"Could not find any clear meanings for '<b>{word}</b>'.", parse_mode=ParseMode.HTML)
                
        elif res.status_code == 404:
            msg.reply_text(f"Could not find a definition for '<b>{word}</b>'. Please check your spelling!", parse_mode=ParseMode.HTML)
        else:
            msg.reply_text("The dictionary service is currently acting up. Please try again later!")

    except requests.exceptions.Timeout:
        msg.reply_text("⏳ Connection timed out. The dictionary API took too long to respond.")
    except requests.exceptions.RequestException:
        msg.reply_text("🔌 Failed to connect to the dictionary service. It might be down temporarily.")

# Metadata for help commands (standard pattern in many modular bot bases)
__help__ = """
*User Commands:*
» `/define <word>`: Looks up the English dictionary definition of a word.
"""

__mod_name__ = "Dictionary"

# Register the Command Handler to the Dispatcher
DEFINE_HANDLER = CommandHandler("define", define, pass_args=True)
dispatcher.add_handler(DEFINE_HANDLER)
