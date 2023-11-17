from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from connections import ConnectionsResult


async def post_stats(context: ContextTypes.DEFAULT_TYPE, puzzle_data, puzzle_num: int, chat_id: int):
    players_by_guesses = [0] * 5

    for user, num_incorrect_guesses in puzzle_data.items():
        players_by_guesses[num_incorrect_guesses] += 1
    num_players = sum(players_by_guesses)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
Connections
Puzzle \\#{puzzle_num}

💯 Perfect: **{players_by_guesses[0]}** \\({players_by_guesses[0] / num_players:.0%}\\)
🟨 1 Guess: **{players_by_guesses[1]}** \\({players_by_guesses[1] / num_players:.0%}\\)
🟩 2 Guess: **{players_by_guesses[2]}** \\({players_by_guesses[2] / num_players:.0%}\\)
🟦 3 Guess: **{players_by_guesses[3]}** \\({players_by_guesses[3] / num_players:.0%}\\)
🟪 4 Guess: **{players_by_guesses[4]}** \\({players_by_guesses[4] / num_players:.0%}\\)
""",
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def handle_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    result: ConnectionsResult,
):
    context.chat_data[result.puzzle_num][update.effective_user.id] = result.num_guesses_incorrect

    if result.num_guesses_incorrect == 0:
        response = "💯 Perfect!"
    elif result.num_guesses_incorrect == 4:
        response = "🫡 Nice try"
    else:
        response = "👍 Good job"

    await update.message.reply_text(response)



