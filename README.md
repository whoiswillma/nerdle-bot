# Nerdle Telegram Bot 🤓

A bare-bones telegram bot for groups to keep tabs on [Connections](https://www.nytimes.com/games/connections).

### What it does

Replies to you when you post results.

```
William Ma, [Nov 12, 2023 at 15:08:00]:
Connections 
Puzzle #153
🟦🟦🟦🟦
🟩🟩🟩🟩
🟪🟪🟪🟪
🟨🟨🟨🟨

Nerdle 🤓, [Nov 12, 2023 at 15:08:01]:
💯 Perfect!
```

Gives you stats.

```
William Ma, [Nov 12, 2023 at 15:08:44]:
/stats

Nerdle 🤓, [Nov 12, 2023 at 15:08:45]:
Connections
Puzzle #153

💯 Perfect: 1
👍 Good: 0
```

### Get Started

1. Clone the repository
2. Create a virtual environment (or don't)
   ```sh
   python3 -m venv venv-nerdle
   source venv-nerdle/bin/activate
   ```
3. Install requirements
   ```sh
   pip3 install -r requirements.txt
   ```
4. Create .env file
   ```
   TELEGRAM_BOT_TOKEN="0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefgh"
   ```
5. Run the bot
   ```sh
   python3 main.py  
   ```
