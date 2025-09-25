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
import random

def generate_random_prompt():
    """
    Generates a realistic, cinematic prompt for an AI video model.
    The script randomly selects a scenario type, number of soldiers,
    and other visual elements to create a unique prompt.

    Returns:
        tuple: A tuple containing the scenario type ('injured', 'uninjured', or 'mixed')
               and the generated prompt string.
    """
    # --- Lists of variations (with more than 10 options each) ---
    scenario_type = random.choice(["injured", "uninjured", "mixed", "uninjured", "mixed", "uninjured", "mixed"])
    num_soldiers = random.randint(2, 5)

    camera_heights = [
        "a very high altitude, offering a wide, sweeping view",
        "a medium altitude, providing a detailed view of the terrain",
        "a low altitude",
    ]

    camera_movements = [
        "flying directly overhead on a steady, expansive path",
        "slowly panning across the scene",
        "a slow dolly-in, pushing towards the subject",
        "a subtle orbit shot, circling the soldiers",
        "a static, locked-off camera view from above"
    ]

    time_of_day = [
        "under a brilliant morning sun",
        "in the harsh light of midday",
        "as dusk settles, casting long shadows",
        "in the dead of night, with only moonlight to guide them",
        "during the golden hour, with soft, warm light",
        "just before dawn, with a cold, blue light",
        "at sunset, with vibrant orange and purple hues",
        "under the midday haze, with soft, ambient light",
        "under a full moon, with stark, high-contrast shadows"
    ]

    weather = [
        "with heavy, blowing snow",
        "in a freezing downpour of rain",
        "under a clear, cloudless sky",
        "amidst a swirling sandstorm",
        "with a thick, cold fog rolling in",
        "during a fierce wind, kicking up dust and debris",
        "in a steady, cold drizzle",
        "amidst a light flurry of snowflakes",
        "under a bleak, overcast sky with no rain",
        "in a hazy, humid atmosphere"
    ]

    environments = [
        "a desolate, snow-covered mountain ridge",
        "an arid, rocky desert",
        "a dense, wet spruce forest",
        "a muddy, war-torn battlefield",
        "the cracked, sun-scorched earth of a salt flat",
        "a windswept, icy tundra",
        "a ruined, bombed-out urban landscape",
        "a vast, empty sand dune field",
        "a humid, overgrown jungle clearing",
        "a jagged volcanic landscape with smoking vents"
    ]

    actions = [
        "walking slowly and cautiously",
        "huddled together, looking for warmth",
        "setting up a temporary camp",
        "hiding behind large rocks",
        "crawling slowly towards a makeshift shelter",
        "sprinting from cover to cover",
        "looking through binoculars at a distant point",
        "providing first aid to a comrade",
        "scrambling up a steep incline"
    ]

    injured_body_parts = [
        "arm", "leg", "torso", "head", "shoulder", "back", "foot"
    ]

    injury_severities = [
        "gravely wounded with a makeshift tourniquet applied to his",
        "visibly and severely wounded, with torn clothing and a bloodied",
        "badly bruised and sprained",
        "limping heavily with a fractured",
        "bleeding from a shrapnel wound to his"
    ]

    # --- Construct the base prompt ---
    base_prompt = (
        f"Top-down drone shot from {random.choice(camera_heights)}, {random.choice(camera_movements)}, "
        f"capturing a scene {random.choice(time_of_day)} in {random.choice(weather)}. "
        f"The setting is {random.choice(environments)}. "
        f"Cinematography, hyperrealistic, dramatic, film grain."
    )

    # --- Construct the soldier-specific part of the prompt ---
    soldiers_prompt = ""
    injured_count = 0
    
    if scenario_type == "uninjured":
        soldiers_prompt = f"A squad of {num_soldiers} soldiers are {random.choice(actions)}. They appear to be in good health."
    
    elif scenario_type == "injured":
        injured_count = num_soldiers
    
    elif scenario_type == "mixed":
        injured_count = random.randint(1, num_soldiers - 1)
    
    # Logic for injured and mixed scenarios
    if injured_count > 0:
        injured_prompts = []
        for i in range(injured_count):
            injury_description = f"a soldier lying on the ground, his {random.choice(injured_body_parts)} {random.choice(injury_severities)} {random.choice(injured_body_parts)}."
            injured_prompts.append(injury_description)
        
        uninjured_count = num_soldiers - injured_count
        
        if uninjured_count > 0:
            uninjured_prompts = []
            for i in range(uninjured_count):
                action_description = f"another soldier {random.choice(actions)}"
                uninjured_prompts.append(action_description)
            
            soldiers_prompt = " and ".join(injured_prompts) + ". " + " and ".join(uninjured_prompts)
        else:
            soldiers_prompt = " and ".join(injured_prompts)
        
    final_prompt = f"{base_prompt} The scene shows a group of {num_soldiers} soldiers; {soldiers_prompt}"
    
    return (scenario_type, final_prompt)

        
# Discord Bot Logic
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}!')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def prompt(ctx):
    video_class, prompt_text = await generate_random_prompt()
    await ctx.send(f"## {video_class}##\n`{prompt_text}`")
    
    
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
