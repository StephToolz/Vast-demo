import discord
from discord.ext import commands, tasks
import json
import random
import os
from threading import Thread
from flask import Flask

# 1. SETUP PRO RENDER (Port Scan Timeout fix)
app = Flask('')
@app.route('/')
def home(): return "Rep bot běží!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. NAČTENÍ KONFIGURACE
with open('config.json', 'r') as f:
    config = json.load(f)

# DŮLEŽITÉ: Musíte mít zapnuté 'Server Members Intent' v Developer Portálu!
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. AUTOMATICKÁ SMYČKA
@tasks.loop(minutes=5) # Zde nastavte, jak často má bot psát (minutes=30, hours=1 atd.)
async def auto_rep():
    channel = bot.get_channel(config['channel_id'])
    if channel and channel.guild.members:
        # Vybere náhodného uživatele (ne bota)
        members = [m for m in channel.guild.members if not m.bot]
        if members:
            user = random.choice(members)
            akce = random.choice(["buy", "sell"])
            await channel.send(f"+rep {user.mention} - {akce}")

@auto_rep.before_loop
async def before_auto_rep():
    await bot.wait_until_ready()

# 4. SPUŠTĚNÍ
@bot.event
async def on_ready():
    print(f'Bot {bot.user} odesílá automatické reputace!')
    auto_rep.start()

Thread(target=run_web).start()
bot.run(config['token'])
