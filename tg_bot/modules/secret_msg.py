import uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from tg_bot import dispatcher

# Temporary in-memory database to store secret payloads
# Structure: { secret_id: { "text": secret_text, "target_id": target_user_id, "sender_id": sender_user_id } }
SECRET_DB = {}

def send_secret(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    
    # Check if the user replied to someone
    if not message.reply_to_message:
        message.reply_text("Please reply to the user you want to send a secret message to.")
        return

    # Extract the secret message text (everything after /secret)
    args = context.args
    if not args:
        message.reply_text("Usage: Reply to a user with `/secret <your hidden text>`")
        return
        
    secret_text = " ".join(args)
    target_user = message.reply_to_message.from_user
    sender_user = message.from_user

    if target_user.id == sender_user.id:
        message.reply_text("You can't send a secret message to yourself!")
        return

    # Generate a unique key for this secret instance
    secret_id = str(uuid.uuid4())[:8]

    # Store the payload details
    SECRET_DB[secret_id] = {
        "text": secret_text,
        "target_id": target_user.id,
        "sender_id": sender_user.id
    }

    # Build the interaction layout
    keyboard = [
        [
            InlineKeyboardButton(
                text="👁️ Reveal Secret", 
                callback_data=f"secret_{secret_id}"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Inform the chat a secret message is waiting
    text = (
        f"🔒 *Secret Message For You!*\n\n"
        f"👤 **From:** {sender_user.mention_markdown_v2()}\n"
        f"🎯 **For:** {target_user.mention_markdown_v2()}\n\n"
        f"_Only the intended recipient can read this_."
    )
    
    chat.send_message(text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
    
    # Delete the triggering command to hide the text immediately from plain view
    try:
        message.delete()
    except Exception:
        # Fails silently if the bot isn't granted group admin deletion permissions
        pass


def read_secret(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Extract the unique ID from callback_data (e.g., "secret_abc123" -> "abc123")
    secret_id = query.data.split("_")[1]

    # Handle expired data states
    if secret_id not in SECRET_DB:
        query.answer(text="⚠️ Error: This secret message has expired or no longer exists.", show_alert=True)
        return

    secret_data = SECRET_DB[secret_id]

    # Permission Validation Guard
    if user_id != secret_data["target_id"]:
        query.answer(text="🚫 Imposter alert! This secret message was not meant for you.", show_alert=True)
        return

    # Deliver the secret safely via an inline alert box pop-up
    query.answer(text=f"🔑 Secret:\n\n{secret_data['text']}", show_alert=True)


# Registration components mapped out cleanly for the loading engine
__help__ = """
*Secret Messages:*
 Send a hidden text snippet that can only be unlocked and read by a targeted group member.
 
 • `/secret <text>`: Reply to a user's message to transmit a lockbox packet specifically to them.
"""

__mod_name__ = "Secret Message"

# Wire the actions into your bot's dispatcher instance
dispatcher.add_handler(CommandHandler("secret", send_secret, run_async=True))
dispatcher.add_handler(CallbackQueryHandler(read_secret, pattern=r"^secret_", run_async=True))
