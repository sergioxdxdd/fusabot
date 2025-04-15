from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

TOKEN = "7575065393:AAFgaVU69VzrBo12opWmvwAxAQkk07FRj94"

# --- Base temporal de advertencias ---
warnings = {}

# --- Comandos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy *Fusabot*. Estoy listo para ayudarte con la gestión del grupo.", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Comandos:
/help - Ver esta ayuda
/rules - Ver reglas del grupo
/warn - Advertir a un usuario (responde a su mensaje)
/ban - Banear a un usuario (responde a su mensaje)""")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Reglas del grupo:\n1. Respeto\n2. No spam\n3. No contenido NSFW")

# --- Mensaje de bienvenida con botón ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        keyboard = [[InlineKeyboardButton("Aceptar reglas", callback_data=f"accept_{user.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Bienvenido/a, {user.mention_html()}.\nPor favor, acepta las reglas para participar.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

# --- Acción al apretar botón ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == f"accept_{user_id}":
        await query.answer("¡Gracias por aceptar las reglas!")
        await query.edit_message_text("Acceso concedido.")
    else:
        await query.answer("Este botón no es para vos.", show_alert=True)

# --- Moderación: filtro de enlaces ---
async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "http" in text or "t.me" in text:
        await update.message.delete()

# --- Comando /warn (con 3 strikes) ---
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Responde al mensaje del usuario que querés advertir.")
        return
    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    key = (chat_id, user.id)

    warnings[key] = warnings.get(key, 0) + 1
    count = warnings[key]

    await update.message.reply_text(f"{user.first_name} tiene {count} advertencia(s).")

    if count >= 3:
        await update.message.chat.ban_member(user.id)
        await update.message.reply_text(f"{user.first_name} fue baneado por acumulación de advertencias.")

# --- Comando /ban ---
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Responde al mensaje del usuario que querés banear.")
        return
    user = update.message.reply_to_message.from_user
    await update.message.chat.ban_member(user.id)
    await update.message.reply_text(f"{user.first_name} fue baneado del grupo.")

# --- MAIN ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, filter_links))

print("Fusabot está activo...")
app.run_polling()
