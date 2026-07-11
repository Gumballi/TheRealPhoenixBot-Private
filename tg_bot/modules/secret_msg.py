import uuid
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackContext, CallbackQueryHandler, InlineQueryHandler

from tg_bot import dispatcher

# Internal database for active secrets
SECRET_DB = {}

def escape_markdown_v2(text):
    """Escapes MarkdownV2 special characters to prevent silent formatting crashes."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', str(text))

def inline_secret_handler(update: Update, context: CallbackContext):
    query_obj = update.inline_query
    query_text = query_obj.query.strip()

    if not query_text:
        return

    # Extract all occurrences of @username from the query text
    # Matches standard Telegram usernames: alphanumeric and underscores, 5-32 chars
    target_usernames = set(re.findall(r'@([A-Za-z0-9_]{5,32})', query_text))
    
    # Strip the @usernames out of the query to isolate the clean secret message content
    secret_payload = re.sub(r'@[A-Za-z0-9_]{5,32}', '', query_text).strip()

    if not target_usernames or not secret_payload:
        # Provide an active template hint if they haven't typed text or tagged anyone yet
        results = [
            InlineQueryResultArticle(
                id="hint",
                title="Secret Message Format Guide",
                description="Type: <secret text> @user1 @user2",
                input_message_content=InputTextMessageContent(
                    "Usage: Type your secret message followed by the @username tags of who can read it."
                )
            )
        ]
        context.bot.answer_inline_query(query_obj.id, results, cache_time=1)
        return

    # Normalize extracted target strings to lowercase for strict validation comparison matches
    target_usernames = {user.lower() for user in target_usernames}
    sender = query_obj.from_user

    # Generate tracking keys
    secret_id = str(uuid.uuid4())[:8]
    SECRET_DB[secret_id] = {
        "text": secret_payload,
        "targets": target_usernames,
        "sender_id": sender.id
    }

    # Setup the interactive buttons
    keyboard = [
        [
            InlineKeyboardButton(
                text="👁️ Reveal Secret", 
                callback_data="secret_{}".format(secret_id)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Frame safe output layout strings
    safe_sender_name = escape_markdown_v2(sender.first_name)
    formatted_targets = ", ".join(["@{}".format(escape_markdown_v2(u)) for u in target_usernames])

    display_text = (
        "🔒 *A Secret Message Has Arrived\\!*\n\n"
        "👤 *From:* [{}](tg://user?id={})\n"
        "🎯 *For:* {}\n\n"
        "_Only designated recipients can open this text frame\\._"
    ).format(safe_sender_name, sender.id, formatted_targets)

    # Truncate descriptions nicely for the inline keyboard choice deck UI
    desc_snippet = secret_payload[:25] + "..." if len(secret_payload) > 25 else secret_payload

    results = [
        InlineQueryResultArticle(
            id=secret_id,
            title="Send Encrypted Capsule",
            description="Message: {}".format(desc_snippet),
            input_message_content=InputTextMessageContent(
                message_text=display_text, 
                parse_mode="MarkdownV2"
            ),
            reply_markup=reply_markup
        )
    ]

    context.bot.answer_inline_query(query_obj.id, results, cache_time=0, is_personal=True)


def read_inline_secret(update: Update, context: CallbackContext):
    query = update.callback_query
    current_user = query.from_user
    
    secret_id = query.data.split("_")[1]

    if secret_id not in SECRET_DB:
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="⚠️ Error: This secret envelope has expired or no longer exists.", 
            show_alert=True
        )
        return

    data = SECRET_DB[secret_id]
    current_username = (current_user.username or "").lower()

    # Permission validation check across all allowed users inside the collection array
    if current_username not in data["targets"] and current_user.id != data["sender_id"]:
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="🚫 Access Denied! Your username is not authorized to read this secret capsule.", 
            show_alert=True
        )
        return

    # Push verification contents out directly into popup windows
    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text="🔑 Decrypted Secret Message:\n\n{}".format(data['text']), 
        show_alert=True
    )


# Wire handlers cleanly into the central framework engine layers
dispatcher.add_handler(InlineQueryHandler(inline_secret_handler))
dispatcher.add_handler(CallbackQueryHandler(read_inline_secret, pattern=r"^secret_"))
