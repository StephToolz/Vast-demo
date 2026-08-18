import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from threading import Thread
from flask import Flask
from datetime import datetime

# 1. SETUP PRO RENDER (Oprava Port Scan Timeout)
app = Flask('')
@app.route('/')
def home(): return "CS2 Proof & Rep Bot is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. DEFINICE DŮVODŮ (Tvé původní CS2 důvody)
duvody = [
    "fast and legit trade ++",
    "vouch, skins received instantly",
    "smooth deal, very safe trader",
    "sent first and he delivered, big vouch",
    "legit staff, helped me with the trade",
    "top tier trader, no scam here",
    "best prices for skins, definitely recommend",
    "fast payment, clean trade",
    "everything went smooth, +rep",
    "vouch +1, very friendly and fast",
    "safe trade, no midman needed",
    "trusted member, easy trade",
    "clean trade, would deal with him again",
    "awesome prices, huge vouch for this guy"
]

# 3. NASTAVENÍ BOTA A INTENTS
# Musíš mít zapnutý 'Server Members Intent' v Discord Developer Portálu!
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=intents)

    async def setup_hook(self):
        # Synchronizace slash příkazů
        await self.tree.sync()
        print("Slash příkazy synchronizovány!")

bot = MyBot()

# 4. POMOCNÉ FUNKCE
def get_header(jmeno):
    """Formát hlavičky podle tvých předloh [1], [2]"""
    cas = datetime.now().strftime("%H:%M")
    return f"{cas} dop. **{jmeno}**"

# 5. AUTOMATICKÁ SMYČKA (Opravená logika)
@tasks.loop(hours=1)
async def auto_rep():
    try:
        # Načtení ID kanálu z Environment Variables nebo configu
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        channel_id = int(config['channel_id'])
        channel = bot.get_channel(channel_id)
        
        if channel is None:
            print(f"DEBUG: Kanál {channel_id} nenalezen!")
            return

        # Získání členů (vyžaduje Members Intent)
        members = [m for m in channel.guild.members if not m.bot]
        if not members:
            print("DEBUG: Žádní členové k výběru.")
            return

        user = random.choice(members)
        vybrany_rep = random.choice(duvody)
        
        # Odeslání zprávy
        await channel.send(f"+rep {user.mention} - {vybrany_rep}")
        print(f"DEBUG: Úspěšně odeslán rep pro {user.name}")

    except Exception as e:
        print(f"LOG CHYBA v auto_rep: {e}")

@auto_rep.before_loop
async def before_auto_rep():
    await bot.wait_until_ready()

# 6. PŘÍKAZY (Nitro, PayPal, Rep)

@bot.tree.command(name="nitro", description="Generates a fake Nitro gift proof")
async def nitro_slash(interaction: discord.Interaction, jmeno: str, zprava: str = "Enjoy your gift!"):
    """Simuluje Nitro gift podle tvých zdrojů [3], [4]"""
    if not os.path.exists("blankgift.png"):
        await interaction.response.send_message("Chyba: blankgift.png chybí!", ephemeral=True)
        return

    file = discord.File("blankgift.png", filename="nitro.png")
    embed = discord.Embed(
        title="You've been gifted a subscription!",
        description=f"**{jmeno}** has gifted you Nitro for 1 month!",
        color=0x242429
    )
    embed.set_image(url="attachment://nitro.png")
    await interaction.response.send_message(content=f"{get_header(jmeno)}\n{zprava}", file=file, embed=embed)

@bot.command()
async def paypal(ctx, jmeno: str, castka: str):
    """Falešné potvrzení PayPal platby [5], [6]"""
    embed = discord.Embed(title="Transaction Successful", description=f"Received **{castka}** from **{jmeno}**", color=0x0070ba)
    await ctx.send(content=get_header(jmeno), embed=embed)

# 7. SPUŠTĚNÍ
@bot.event
async def on_ready():
    print(f'Bot {bot.user} je připraven na CS2 serveru!')
    if not auto_rep.is_running():
        auto_rep.start()

# Načtení tokenu z prostředí Renderu (os.environ) pro maximální bezpečnost
TOKEN = os.environ.get('DISCORD_TOKEN')

Thread(target=run_web).start()
bot.run(TOKEN)
