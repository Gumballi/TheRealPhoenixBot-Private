import uuid
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackQueryHandler, InlineQueryHandler

from tg_bot import dispatcher

SECRET_DB = {}

def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', str(text))

def inline_secret_handler(update, context):
    query_obj = update.inline_query
    query_text = query_obj.query.strip()

    if not query_text:
        return

    # Extract all @username handles
    target_usernames = set(re.findall(r'@([A-Za-z0-9_]{5,32})', query_text))
    secret_payload = re.sub(r'@[A-Za-z0-9_]{5,32}', '', query_text).strip()

    if not target_usernames or not secret_payload:
        results = [
            InlineQueryResultArticle(
                id="hint",
                title="Secret Message Guide",
                description="Type: secret text @username",
                input_message_content=InputTextMessageContent(
                    "Usage: Type your secret message followed by the @username tags."
                )
            )
        ]
        query_obj.answer(results, cache_time=1)
        return

    target_usernames = {user.lower() for user in target_usernames}
    sender = query_obj.from_user
    secret_id = str(uuid.uuid4())[:8]
    
    SECRET_DB[secret_id] = {
        "text": secret_payload,
        "targets": target_usernames,
        "sender_id": sender.id
    }

    keyboard = [[InlineKeyboardButton(text="👁️ Reveal Secret", callback_data="secret_{}".format(secret_id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    safe_sender_name = escape_markdown_v2(sender.first_name)
    formatted_targets = ", ".join(["@{}".format(escape_markdown_v2(u)) for u in target_usernames])

    display_text = (
        "🔒 *A Secret Message Has Arrived\\!*\n\n"
        "👤 *From:* [{}](tg://user?id={})\n"
        "🎯 *For:* {}\n\n"
        "_Only designated recipients can open this text frame\\._"
    ).format(safe_sender_name, sender.id, formatted_targets)

    results = [
        InlineQueryResultArticle(
            id=secret_id,
            title="Send Encrypted Capsule",
            description="Message: {}...".format(secret_payload[:25]),
            input_message_content=InputTextMessageContent(
                message_text=display_text, 
                parse_mode="MarkdownV2"
            ),
            reply_markup=reply_markup
        )
    ]
    query_obj.answer(results, cache_time=0, is_personal=True)

def read_inline_secret(update, context):
    query = update.callback_query
    current_user = query.from_user
    secret_id = query.data.split("_")[1]

    if secret_id not in SECRET_DB:
        query.answer(text="⚠️ Error: This secret envelope has expired or no longer exists.", show_alert=True)
        return

    data = SECRET_DB[secret_id]
    current_username = (current_user.username or "").lower()

    if current_username not in data["targets"] and current_user.id != data["sender_id"]:
        query.answer(text="🚫 Access Denied! Your username is not authorized to read this.", show_alert=True)
        return

    query.answer(text="🔑 Decrypted Secret Message:\n\n{}".format(data['text']), show_alert=True)

dispatcher.add_handler(InlineQueryHandler(inline_secret_handler, run_async=True))
dispatcher.add_handler(CallbackQueryHandler(read_inline_secret, pattern=r"^secret_", run_async=True))
