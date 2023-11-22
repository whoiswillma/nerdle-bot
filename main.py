import datetime
import logging
import os

import dotenv
from pytz import timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, PicklePersistence

import v0.handlers
import v1.handlers
from connections import parse_connections_results

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

timezone_pt = timezone('US/Pacific')
connections_zero = datetime.datetime(2023, 6, 11, tzinfo=timezone_pt)


def puzzle_number_now() -> int:
    return (datetime.datetime.now(tz=timezone_pt) - connections_zero).days


def puzzle_data_version(puzzle_data) -> int:
    version = None

    if 'version' not in puzzle_data:
        version = 0
    elif puzzle_data['version'] == 1:
        version = 1
    else:
        raise RuntimeError(f"Unrecognized version \"{puzzle_data['version']}\"")

    logging.info(f"Parsed puzzle data version {version}")

    return version


async def post_stats(
    context: ContextTypes.DEFAULT_TYPE,
    puzzle_num: int,
    chat_data,
    chat_id: int
):
    if puzzle_num not in chat_data or not chat_data[puzzle_num]:
        logger.warning(f"No puzzle data for puzzle #{puzzle_num}, chat id {chat_id}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"No stats for Puzzle #{puzzle_num}"
        )
        return

    puzzle_data = chat_data[puzzle_num]
    version = puzzle_data_version(puzzle_data)
    if version == 0:
        await v0.handlers.post_stats(context, puzzle_data, puzzle_num, chat_id)
    elif version == 1:
        await v1.handlers.post_stats(context, puzzle_data, puzzle_num, chat_id)


async def _post_stats_job(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data

    await post_stats(
        context,
        puzzle_num=job_data['puzzle_num'],
        chat_data=job_data['chat_data'],
        chat_id=context.job.chat_id
    )


def post_stats_job_datetime() -> datetime.datetime:
    if os.getenv('MODE') == 'DEBUG':
        return datetime.datetime.now(tz=timezone_pt) + datetime.timedelta(seconds=15)

    else:
        dt = datetime.datetime.now(tz=timezone_pt)
        dt += datetime.timedelta(days=1)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt


async def schedule_post_stats_job(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    post_stats_job_name = f"post_stats chat_id={chat_id}"

    for job in context.job_queue.get_jobs_by_name(post_stats_job_name):
        job.enabled = False
        job.schedule_removal()

    context.job_queue.run_once(
        _post_stats_job,
        when=post_stats_job_datetime(),
        data={
            'chat_data': context.chat_data,
            'puzzle_num': puzzle_number_now(),
        },
        name=post_stats_job_name,
        chat_id=chat_id
    )


async def handle_easter_egg_salute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    positions = {'lieutenant', 'captain', 'major', 'colonel', 'kernel', 'general'}
    message = update.message.text.lower()
    if any(position in message for position in positions):
        await update.message.reply_text("🫡")


async def handle_connections_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = parse_connections_results(update.message.text)
    if not result:
        return None

    puzzle_num = result.puzzle_num
    if puzzle_num not in context.chat_data:
        context.chat_data[puzzle_num] = {
            'version': 1,
            'players': {},
        }

    puzzle_data = context.chat_data[puzzle_num]
    version = puzzle_data_version(puzzle_data)
    if version == 0:
        await v0.handlers.handle_result(update, context, result)
    elif version == 1:
        await v1.handlers.handle_result(update, context, result)

    await schedule_post_stats_job(context, update.effective_chat.id)


async def parse_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_connections_results(update, context)
    await handle_easter_egg_salute(update, context)


async def command_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if len(context.args) == 0:
        puzzle_num = puzzle_number_now()
    elif len(context.args) == 1 and context.args[0].isdigit():
        puzzle_num = int(context.args[0])
    else:
        puzzle_num = puzzle_number_now()

    if not context.chat_data:
        logger.warning(f"No chat data for chat id {chat_id}")
        return

    await post_stats(
        context,
        puzzle_num=puzzle_num,
        chat_data=context.chat_data,
        chat_id=chat_id
    )


def main():
    dotenv.load_dotenv()

    logging.info(f"MODE = {os.getenv('MODE')}")

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
