import os
import discord
from discord.ext import commands
import aiohttp
import asyncio
import random

# This is a simple web server to keep the bot alive on Render
async def keep_alive():
    async with aiohttp.web.Application() as app:
        async def alive_handler(request):
            return aiohttp.web.Response(text="Discord bot is alive!")
        app.router.add_get('/', alive_handler)
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 3000))
        await site.start()

# Discord Bot Logic
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}!')
    print('------')

# List of random words for the bot to choose from
random_words = ["apple", "banana", "cherry", "dragon", "echo", "foxtrot", "glove", "hat"]

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def prompt(ctx):
    await ctx.send(random.choice(random_words))

# Main function to run the bot and the web server
async def main():
    # Get the bot token from environment variables
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found.")
        return

    await asyncio.gather(
        keep_alive(),
        bot.start(token)
    )

if __name__ == "__main__":
    asyncio.run(main())

