from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, JobQueue
import datetime
import json

# קובץ לשמירת ה-Chat IDs
CHAT_IDS_FILE = "chat_ids.json"

# פונקציה לשמירת ה-Chat IDs בקובץ
def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as file:
        json.dump(chat_ids, file)

# פונקציה לטעינת ה-Chat IDs מקובץ
def load_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# פונקציה שמוסיפה קבוצה לרשימה אם הבוט נוסף
def add_chat(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat_ids = load_chat_ids()

    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)
        update.message.reply_text("✅ הקבוצה נוספה לרשימת השידור!")

# פונקציה שמסירה קבוצה מהרשימה כשהבוט עוזב
def remove_chat(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat_ids = load_chat_ids()

    if update.message.left_chat_member and update.message.left_chat_member.id == context.bot.id:
        if chat_id in chat_ids:
            chat_ids.remove(chat_id)
            save_chat_ids(chat_ids)
            print(f"📢 הבוט הוסר מהקבוצה {chat_id}, והיא נמחקה מהרשימה.")

# פונקציה ששולחת הודעה לכל הקבוצות
def send_sunday_message(context: CallbackContext) -> None:
    chat_ids = load_chat_ids()
    message = "Happy Sunday to all 😎\nPlease share what geos you need for tmrw :)"

    for chat_id in chat_ids:
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"⚠️ שגיאה בשליחת הודעה ל-{chat_id}: {e}")

# פונקציה ששולחת הודעה שהבוט מוכן לעבוד כל יום ב-11:30
def send_ready_message(context: CallbackContext) -> None:
    chat_ids = load_chat_ids()
    message = "אני מוכן לעבוד! 😎"

    for chat_id in chat_ids:
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"⚠️ שגיאה בשליחת הודעה ל-{chat_id}: {e}")

# תזמון הודעה ליום ראשון ב-11:00
def schedule_sunday_message(job_queue: JobQueue):
    now = datetime.datetime.now()
    next_sunday = now + datetime.timedelta((6 - now.weekday()) % 7)
    send_time = next_sunday.replace(hour=11, minute=0, second=0, microsecond=0)

    job_queue.run_repeating(send_sunday_message, interval=7*24*60*60, first=send_time)

# תזמון הודעה כל יום ב-11:30
def schedule_daily_ready_message(job_queue: JobQueue):
    # זמן של 11:30 כל יום
    time = datetime.time(hour=11, minute=30)

    # תזמון ההודעה כל יום ב-11:30
    job_queue.run_daily(send_ready_message, time)

# 🔹 פקודה חדשה: הצגת רשימת הקבוצות שהבוט משדר אליהן
def list_groups(update: Update, context: CallbackContext):
    chat_ids = load_chat_ids()

    # בדיקה שהפקודה נשלחה בצ'אט פרטי
    if update.message.chat.type != "private":
        update.message.reply_text("❌ פקודה זו זמינה רק בצ'אט פרטי עם הבוט.")
        return

    if not chat_ids:
        update.message.reply_text("📭 הבוט כרגע לא מחובר לאף קבוצה.")
    else:
        groups_list = "\n".join([f"• {chat_id}" for chat_id in chat_ids])
        update.message.reply_text(f"📋 רשימת הקבוצות שהבוט משדר אליהן:\n{groups_list}")

def main():
    TOKEN = "7135528210:AAHMCoKy_UUM8rPoaHaRuqDnIakOPvlhnzY"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    # מאזין להוספת הבוט לקבוצה
    dp.add_handler(MessageHandler(Filters.chat_type.groups, add_chat))

    # מאזין להסרת הבוט מקבוצה
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, remove_chat))

    # מאזין לפקודה /list (רק בצ'אט פרטי)
    dp.add_handler(CommandHandler("list", list_groups))

    # תזמון הודעה ליום ראשון
    schedule_sunday_message(job_queue)

    # תזמון הודעה כל יום ב-11:30
    schedule_daily_ready_message(job_queue)

    # התחל את הבוט
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
