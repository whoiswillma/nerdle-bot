import datetime
import logging
import os

import dotenv
import telegram
from pytz import timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, PicklePersistence

import connections

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

timezone_pt = timezone('US/Pacific')


async def post_stats(context: ContextTypes.DEFAULT_TYPE, chat_data, chat_id: int):
    puzzle_num = max(chat_data.keys())
    if not chat_data[puzzle_num]:
        logger.warning(f"No chat data for puzzle #{puzzle_num}, chat id {chat_id}")
        return

    puzzle_data = chat_data[puzzle_num]
    num_players = num_perfect = num_good = 0

    for user, num_incorrect_guesses in puzzle_data.items():
        num_players += 1
        if num_incorrect_guesses == 0:
            num_perfect += 1
        elif num_incorrect_guesses < 4:
            num_good += 1

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
Connections
Puzzle \\#{puzzle_num}

💯 Perfect: **{num_perfect}**
👍 Good: **{num_good}**
""",
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
    )


async def _post_stats_job(context: ContextTypes.DEFAULT_TYPE):
    await post_stats(context, chat_data=context.job.data, chat_id=context.job.chat_id)


async def parse_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = connections.parse_connections_results(update.message.text)
    if not result:
        return None

    if result.puzzle_num not in context.chat_data:
        context.chat_data[result.puzzle_num] = {}
    context.chat_data[result.puzzle_num][update.effective_user.id] = result.num_guesses_incorrect

    if result.num_guesses_incorrect == 0:
        response = "💯 Perfect!"
    elif result.num_guesses_incorrect == 4:
        response = "🫡 Nice try"
    else:
        response = "👍 Good job"

    await update.message.reply_text(response)

    post_stats_job_name = f"post_stats chat_id={update.effective_chat.id}"

    for job in context.job_queue.get_jobs_by_name(post_stats_job_name):
        job.enabled = False
        job.schedule_removal()

    dt = datetime.datetime.now(tz=timezone_pt)
    dt += datetime.timedelta(days=1)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    context.job_queue.run_once(
        _post_stats_job,
        when=dt,
        data=context.chat_data,
        name=post_stats_job_name,
        chat_id=update.effective_chat.id
    )


async def command_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.chat_data:
        logger.warning(f"No chat data for chat id {chat_id}")
        return

    await post_stats(context, chat_data=context.chat_data, chat_id=chat_id)


def main():
    dotenv.load_dotenv()

    persistence = PicklePersistence(filepath="data.pickle")
    application = (
        Application
            .builder()
            .persistence(persistence)
            .token(os.environ.get("TELEGRAM_BOT_TOKEN"))
            .build()
    )

    application.add_handler(CommandHandler("stats", command_stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()