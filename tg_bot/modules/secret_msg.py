import uuid
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackContext, CallbackQueryHandler, InlineQueryHandler

from tg_bot import dispatcher

# Internal dictionary database for active secrets
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

    # Regex looks for: <any secret text> followed by space and @username at the end
    match = re.search(r'(.*?)\s+@([A-Za-z0-9_]{5,32})$', query_text)
    
    if not match:
        results = [
            InlineQueryResultArticle(
                id="hint",
                title="Secret Message Format Guide",
                description="Type: your message here @username",
                input_message_content=InputTextMessageContent(
                    "To send a secret, type: @botusername <secret text> @target_username"
                )
            )
        ]
        context.bot.answer_inline_query(query_obj.id, results, cache_time=1)
        return

    secret_payload = match.group(1).strip()
    target_username = match.group(2).strip().lower()
    sender = query_obj.from_user

    # Create reference tracking keys
    secret_id = str(uuid.uuid4())[:8]
    SECRET_DB[secret_id] = {
        "text": secret_payload,
        "target_username": target_username,
        "sender_id": sender.id
    }

    # Build the interactive panel buttons
    keyboard = [
        [
            InlineKeyboardButton(
                text="👁️ Reveal Secret", 
                callback_data="secret_{}".format(secret_id)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Safely escape usernames and display strings for MarkdownV2 compliance
    safe_sender_name = escape_markdown_v2(sender.first_name)
    safe_target_user = escape_markdown_v2(target_username)

    display_text = (
        "🔒 *A Secret Message Has Arrived\\!*\n\n"
        "👤 *From:* [{}](tg://user?id={})\n"
        "🎯 *For:* @{}\n\n"
        "_Only the designated recipient can open this text frame\\._"
    ).format(safe_sender_name, sender.id, safe_target_user)

    results = [
        InlineQueryResultArticle(
            id=secret_id,
            title="Send secret capsule to @{}".format(target_username),
            description="Message snippet: {}...".format(secret_payload[:25]),
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

    # Permission check validation
    if current_username != data["target_username"]:
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="🚫 Access Denied! This secret capsule is strictly for @{}.".format(data['target_username']), 
            show_alert=True
        )
        return

    # Deliver content securely via popup
    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text="🔑 Decrypted Secret Message:\n\n{}".format(data['text']), 
        show_alert=True
    )


# Attach handlers to the central dispatcher
dispatcher.add_handler(InlineQueryHandler(inline_secret_handler))
dispatcher.add_handler(CallbackQueryHandler(read_inline_secret, pattern=r"^secret_"))
