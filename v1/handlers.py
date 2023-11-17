from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from connections import SpecialOrder, ConnectionsResult


async def post_stats(
    context: ContextTypes.DEFAULT_TYPE,
    puzzle_data,
    puzzle_num: int,
    chat_id: int,
):
    num_players = len(puzzle_data['players'])

    players_by_guesses = [0] * 5
    for user_id, player_data in puzzle_data['players'].items():
        players_by_guesses[player_data.get('num_guesses_incorrect', 0)] += 1

    num_forward_order = sum(
        player_data['special_order'] == SpecialOrder.NATURAL_ORDER
        for user_id, player_data in puzzle_data['players'].items()
    )
    num_reverse_order = sum(
        player_data['special_order'] == SpecialOrder.REVERSE_ORDER
        for user_id, player_data in puzzle_data['players'].items()
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
Connections
Puzzle \\#{puzzle_num}

💯 Perfect: {players_by_guesses[0]} \\({players_by_guesses[0] / num_players:.0%}\\)
🟨 1 Guess: {players_by_guesses[1]} \\({players_by_guesses[1] / num_players:.0%}\\)
🟩 2 Guess: {players_by_guesses[2]} \\({players_by_guesses[2] / num_players:.0%}\\)
🟦 3 Guess: {players_by_guesses[3]} \\({players_by_guesses[3] / num_players:.0%}\\)
🟪 4 Guess: {players_by_guesses[4]} \\({players_by_guesses[4] / num_players:.0%}\\)

➡️ Forward: {num_forward_order}
↩️ Reverse: {num_reverse_order}
""",
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def handle_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    result: ConnectionsResult,
):
    context.chat_data[result.puzzle_num]['players'][update.effective_user.id] = {
        'num_guesses_incorrect': result.num_guesses_incorrect,
        'special_order': result.special_order,
    }

    if result.num_guesses_incorrect == 0:
        response = "💯 Perfect!"
    elif result.num_guesses_incorrect == 4:
        response = "🫡 Nice try"
    else:
        response = "👍 Good job"

    if result.special_order == SpecialOrder.NATURAL_ORDER:
        response += " (➡️ Forward Order)"
    elif result.special_order == SpecialOrder.REVERSE_ORDER:
        response += " (↩️ Reverse Order)"

    await update.message.reply_text(response)

