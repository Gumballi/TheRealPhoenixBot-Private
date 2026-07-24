import re
import uuid
from telegram import (
    Bot, 
    Update, 
    InlineQueryResultArticle, 
    InputTextMessageContent, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ParseMode
)
from telegram.ext import InlineQueryHandler, CallbackQueryHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler

# Shared memory dictionary to store whispers in RAM
# Key: UUID (string), Value: Dictionary containing sender, target, and text
WHISPERS = {}


@run_async
def inline_whisper(bot: Bot, update: Update):
    """Handles the creation of the whisper via inline query typing."""
    query = update.inline_query.query
    
    # Check if the user is typing in the correct format: @username message
    match = re.match(r"^@?([\w_]+)\s+(.+)", query)
    
    if not match:
        # If they haven't typed a full format yet, show a placeholder
        placeholder = InlineQueryResultArticle(
            id=uuid.uuid4().hex[:10],
            title="How to send a whisper",
            description="Type: @username Your secret message here",
            input_message_content=InputTextMessageContent(
                "🤫 To use the whisper feature, type `@botusername @target_user Your secret message`",
                parse_mode=ParseMode.MARKDOWN
            )
        )
        bot.answer_inline_query(update.inline_query.id, [placeholder], cache_time=0)
        return

    target_username = match.group(1).lower()
    secret_message = match.group(2)
    
    sender_id = update.inline_query.from_user.id
    
    # Generate a unique, short ID for this specific whisper
    whisper_id = uuid.uuid4().hex[:10]
    
    # Store it in memory
    WHISPERS[whisper_id] = {
        "sender_id": sender_id,
        "target_username": target_username,
        "message": secret_message
    }

    # Build the display text for the chat
    display_text = (
        f"🤫 **A Secret Whisper**\n\n"
        f"👤 **To:** @{target_username}\n"
        f"🔒 *This message is cryptographically locked. Only the intended recipient can open it.*"
    )

    # Build the button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 View Whisper", callback_data=f"w_{whisper_id}")]
    ])

    # Send the result back to the user's typing interface
    result = InlineQueryResultArticle(
        id=whisper_id,
        title=f"Send secret whisper to @{target_username}",
        description=f"Message: {secret_message}",
        input_message_content=InputTextMessageContent(display_text, parse_mode=ParseMode.MARKDOWN),
        reply_markup=keyboard
    )

    bot.answer_inline_query(update.inline_query.id, [result], cache_time=0)


@run_async
def whisper_callback(bot: Bot, update: Update):
    """Handles the button click when someone tries to read the whisper."""
    query = update.callback_query
    clicker_id = query.from_user.id
    clicker_username = query.from_user.username.lower() if query.from_user.username else ""

    # Check if this button click belongs to the whisper module
    match = re.match(r"^w_(.+)", query.data)
    if not match:
        return

    whisper_id = match.group(1)
    
    # Handle bot restarts / memory wipes
    if whisper_id not in WHISPERS:
        query.answer("🛑 This whisper has expired or memory was wiped!", show_alert=True)
        return

    whisper = WHISPERS[whisper_id]
    
    # Verify authorization: Allow the sender OR the target to view it
    if clicker_id == whisper["sender_id"] or clicker_username == whisper["target_username"]:
        query.answer(f"🤫 Secret Whisper:\n\n{whisper['message']}", show_alert=True)
    else:
        query.answer(f"🛑 Access Denied!\nThis whisper is exclusively for @{whisper['target_username']}.", show_alert=True)


__help__ = """
Send secret, locked messages to other users that only they can read!

*Usage:*
You don't need to send a command. Just type my username in the chat bar, followed by the target's username and your message.

*Example:*
`@botusername @friendusername Hey, don't tell anyone but...`
"""

__mod_name__ = "Whispers"

# Register the handlers
WHISPER_INLINE_HANDLER = InlineQueryHandler(inline_whisper)
WHISPER_BUTTON_HANDLER = CallbackQueryHandler(whisper_callback, pattern=r"^w_")

dispatcher.add_handler(WHISPER_INLINE_HANDLER)
dispatcher.add_handler(WHISPER_BUTTON_HANDLER)
