import os
import asyncio
import logging
import random
import discord
from discord.ext import commands
from aiohttp import web
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read required env vars
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# This is a simple web server to keep the bot alive on Render
async def start_http_server():
    """
    Initializes and starts the aiohttp web server.
    The server listens on all available interfaces (0.0.0.0)
    and uses the port from the PORT environment variable.
    """
    app = web.Application()
    async def handle_ping(request):
        return web.Response(text="pong")
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"HTTP server running on port {PORT}")
    return runner

# Discord Bot Logic
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

async def main():
    """
    Main function to run both the HTTP server and the Discord bot.
    """
    # Start HTTP server
    runner = await start_http_server()

    # Start the bot with exponential backoff for resilience
    base_delay = 60
    max_delay = 30 * 60
    delay = base_delay

    try:
        while True:
            try:
                logging.info("Starting bot...")
                # The `run` method is a blocking call, use `start` for this aiohttp setup
                await bot.start(TOKEN)
                logging.info("bot.start() returned cleanly; exiting loop.")
                break
            except discord.errors.LoginFailure as e:
                logging.error("Login failed (invalid token). Not retrying. %s", e)
                raise
            except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError, ConnectionResetError, TimeoutError) as e:
                sleep_for = random.randint(15, 30)
                logging.warning("Network error: %s. Retrying in %ss.", e, sleep_for)
                await asyncio.sleep(sleep_for)
            except Exception as e:
                logging.exception("Unexpected error in bot.start(): %s", e)
                await asyncio.sleep(15)

    finally:
        # Clean up HTTP server resources when the bot stops
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
