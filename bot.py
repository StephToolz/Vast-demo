import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from threading import Thread
from flask import Flask
from datetime import datetime

# --- 1. HOSTING SETUP (Render.com) ---
app = Flask('')
@app.route('/')
def home(): return "CS2 High-Realism Bot is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. DYNAMICKÝ GENERÁTOR DŮVODŮ (CS2 & Trading Styl) ---
# Seznamy komponent pro tisíce kombinací inspirované zdroji 5, 6 a 12
adjectives = ["Fast", "Quick", "Smooth", "Legit", "Insane", "Safe", "Best", "Clean", "Trusted", "Instant", "Friendly", "Top"]
verbs = ["trade", "deal", "vouch", "service", "exchange", "transaction", "buy", "sell", "delivery"]
contexts = ["for skins", "with nitro", "via PayPal", "on buff prices", "for the knife", "without middleman", "no scam", "sent first"]
suffixes = ["++", "vouch!", "+rep", "recommended", "big vouch", "safe trader", "thanks!", "5 stars", "everything good"]

def get_realistic_reps(count=500):
    """Vytvoří sadu unikátních kombinací, aby bot nepůsobil podezřele"""
    reps = set()
    while len(reps) < count:
        adj, verb, ctx, suf = random.choice(adjectives), random.choice(verbs), random.choice(contexts), random.choice(suffixes)
        # Různé struktury vět pro přirozený vzhled
        formats = [f"{adj} {verb} {ctx} {suf}", f"{verb} {ctx}, {adj} {suf}", f"{adj} {ctx}, {suf}"]
        reps.add(random.choice(formats))
    return list(reps)

# Při startu vygeneruje 500 unikátních hlášek
duvody = get_realistic_reps(500)

# --- 3. KONFIGURACE BOTA ---
intents = discord.Intents.default()
intents.members = True # Nutné pro výběr náhodných osob ze serveru
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

def get_header(jmeno):
    """Formát: Čas dop. **Jméno** (podle zdroje 1)"""
    cas = datetime.now().strftime("%H:%M")
    return f"{cas} dop. **{jmeno}**"

# --- 4. AUTOMATICKÝ +REP (Každých 5 minut) ---
@tasks.loop(minutes=5)
async def auto_rep():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        channel = bot.get_channel(int(config['channel_id']))
        if channel and channel.guild.members:
            # Vybere náhodného reálného člena serveru
            members = [m for m in channel.guild.members if not m.bot]
            if members:
                user = random.choice(members)
                # Vybere jeden z 500 unikátních vygenerovaných důvodů
                vybrany_rep = random.choice(duvody)
                await channel.send(f"+rep {user.mention} - {vybrany_rep}")
    except Exception as e:
        print(f"Chyba v auto_rep: {e}")

# --- 5. PŘÍKAZY (Nitro, PayPal, Inventory) ---

@bot.command()
async def nitro(ctx, jmeno: str):
    """Generuje Nitro proof s využitím blankgift.png [4, 5]"""
    if not os.path.exists("blankgift.png"):
        return await ctx.send("Chybí blankgift.png!")
    
    file = discord.File("blankgift.png", filename="nitro.png")
    embed = discord.Embed(
        title="You've been gifted a subscription!",
        description=f"**{jmeno}** has gifted you Nitro for 1 month!",
        color=0x242429
    )
    embed.set_image(url="attachment://nitro.png")
    await ctx.send(content=get_header(jmeno), file=file, embed=embed)

@bot.command()
async def paypal(ctx, jmeno: str, castka: str):
    """PayPal transakce [6]"""
    embed = discord.Embed(title="Payment Received", description=f"You received **{castka}** from **{jmeno}**", color=0x0070ba)
    await ctx.send(content=get_header(jmeno), embed=embed)

# --- 6. SPUŠTĚNÍ ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user} běží v CS2 režimu!')
    if not auto_rep.is_running():
        auto_rep.start()

# Načtení tokenu z Environment Variables na Renderu pro bezpečnost [1]
TOKEN = os.environ.get('DISCORD_TOKEN')

Thread(target=run_web).start()
bot.run(TOKEN)
