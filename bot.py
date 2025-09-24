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

async def generate_veo_prompt():
    """
    Generates a video prompt for a Veo 3-like model based on specific
    criteria, including injured soldiers, environment, and camera work.

    Returns:
        tuple: A tuple containing the class (str) and the generated prompt (str).
    """

    # --- Prompt Elements ---
    # Soldier descriptions and gear
    soldiers = [
        "a squad of soldiers in modern combat gear",
        "two special forces operators",
        "a group of exhausted infantrymen",
        "a single soldier with a tactical backpack",
        "an elite sniper team in ghillie suits",
        "a lone medic tending to a fallen comrade",
        "a unit of futuristic soldiers in powered armor",
        "a weary soldier with a dirt-stained face and blank eyes",
    ]

    # Explicit injuries of varying severity
    explicit_injuries = [
        "with a deep laceration on his leg, bleeding visibly",
        "with a severe burn on his arm, skin peeling away",
        "with a bandage wrapped around his head, blood seeping through",
        "with a large shrapnel wound on his torso, struggling to stand",
        "with a torn uniform and a compound fracture in his arm",
        "with a gaping wound on his shoulder, a tourniquet applied hastily",
        "with multiple gunshot wounds to the chest, struggling to breathe",
        "with a disfigured face from a concussive blast",
        "with a shattered kneecap, crawling for cover"]

    # Actions and reactions
    actions_reactions = [
        "reacting to a sudden ambush, taking cover and returning fire",
        "administering first aid to an injured comrade, their faces strained with effort",
        "calling for an emergency medical evacuation, their voices hoarse",
        "making a desperate last stand against overwhelming odds",
        "navigating through dense wreckage, inspecting the damage",
        "clearing a building room-by-room, guns up and alert",
        "sharing a moment of quiet reflection, sitting against a wall",
        "reacting to the sound of an approaching enemy patrol, freezing in place",
        "hiding in the shadows, listening to enemy comms",
        "reloading their rifle while maintaining a defensive position",
        "pulling a fallen comrade to safety under heavy fire",
        "setting up a defensive perimeter and checking their gear",
        "on patrol, scanning the horizon for any sign of movement",
        "resting in a bombed-out building, sharing MREs and water",
    ]

    # Environments
    environments = [
        "in a desolate, war-torn desert",
        "in the dense undergrowth of a jungle",
        "in the crumbling ruins of a cityscape",
        "on a rocky, snow-covered mountain ridge",
        "inside a dimly lit, abandoned bunker",
        "in a flooded, swampy forest",
        "on a desolate, windswept coastline",
        "in a dense, forgotten bamboo forest",
        "in a futuristic, neon-lit urban warzone",
        "inside a dusty, collapsed subway tunnel",
    ]

    # Times of day
    times_of_day = [
        "at night",
        "at dawn",
        "in the evening",
        "in the middle of the day",
        "at dusk",
        "just before midnight",
        "in the early morning",
        "at high noon",
    ]

    # Weather conditions
    weather_conditions = [
        "in heavy rain",
        "with a heavy fog rolling in",
        "with a sandstorm brewing",
        "under clear weather",
        "with light snowfall",
        "during a fierce thunderstorm with lightning and thunder",
        "under a cold, bone-chilling mist",
        "with a light, but steady drizzle",
        "under the scorching sun",
    ]

    # Camera movements and perspectives
    camera_options = [
        "an aerial shot, slowly panning across the scene",
        "a low-angle tracking shot, following the soldiers",
        "a high-angle shot, looking down on the action",
        "a slow cinematic pan across the group",
        "a handheld camera, slightly shaky and close-up",
        "a static wide shot showing the entire scene",
        "a dolly zoom shot, with the background changing perspective",
        "a quick zoom-in to a soldier's face, highlighting emotion",
        "a circular tracking shot around the group of soldiers",
    ]

    # --- Weighted Random Selection ---
    # The ratio for uninjured:mixed:injured is 1:2:2.
    # The weights for random.choices should reflect this ratio.
    prompt_classes = ["uninjured", "mixed", "injured"]
    weights = [1, 2, 2]
    video_class = random.choices(prompt_classes, weights=weights, k=1)[0]

    # --- Prompt Construction ---
    soldier_subject = random.choice(soldiers)
    action_reaction = random.choice(actions_reactions)
    camera = random.choice(camera_options)
    
    # Cyclical environment selection
    # Using a list with indices allows us to ensure each category is always used.
    environment = random.choice(environments)
    time = random.choice(times_of_day)
    weather = random.choice(weather_conditions)
    environment_string = f"{environment} {time} {weather}"

    # Build the prompt based on the chosen class
    if video_class == "injured":
        injury = random.choice(explicit_injuries)
        prompt = f"A realistic cinematic video of {soldier_subject} {injury}, {action_reaction}. The scene takes place {environment_string}. The camera is {camera}."
    
    elif video_class == "mixed":
        # A mixed prompt needs at least two soldiers to work effectively
        if len(soldiers) == 1:
            soldier_subject = random.choice([
                "a squad of soldiers",
                "two special forces operators",
                "a group of infantrymen"
            ])
        
        injury = random.choice(explicit_injuries)
        prompt = f"A realistic cinematic video of {soldier_subject}, one of them {injury}, {action_reaction}. The scene takes place {environment_string}. The camera is {camera}."

    else: # Uninjured
        prompt = f"A realistic cinematic video of {soldier_subject} {action_reaction}. The scene takes place {environment_string}. The camera is {camera}."
        
    return (video_class, prompt)

        
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
    video_class, prompt_text = await generate_veo_prompt()
    await ctx.send(f"##{video_class}##\n`{prompt_text}`")
    
    
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
