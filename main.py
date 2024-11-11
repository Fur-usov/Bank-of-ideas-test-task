import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
#import logging

# Словарь для хранения соответствия между пользователями и администратором
user_to_admin = {}
admin_id = '1234'  # Замените на фактический ID администратора

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Отправьте сообщение, и администратор его получит.")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if str(user_id) not in user_to_admin:
        user_to_admin[str(user_id)] = update.message.chat_id
    
    await context.bot.send_message(chat_id=admin_id, text=f"Сообщение от {user_id}: {update.message.text}")

async def forward_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == int(admin_id):
        # Ожидается, что администратор отправляет в формате "user_id сообщение"
        try:
            user_id, message = update.message.text.split(maxsplit=1)
            user_chat_id = user_to_admin.get(user_id)
            if user_chat_id:
                await context.bot.send_message(chat_id=user_chat_id, text=message)
            else:
                await update.message.reply_text("Некорректный пользователь или пользователь не в сети.")
        except ValueError:
            await update.message.reply_text("Пожалуйста, используйте формат: 'user_id сообщение'.")

def main() -> None:
    # Создайте приложение и передайте токен вашего бота
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=int(admin_id)), forward_to_user))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
