import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
from dotenv import load_dotenv
import os
import io
import asyncio
import aiohttp
from keep_alive import keep_alive


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
keep_alive()

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.command(name = "hello_angela")
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}! My name is Angela and it's nice to meet you")

@bot.command(name="angela_find_user")
async def find_user(ctx, user_id: int):
    user = ctx.guild.get_member(user_id)

    if user:
        await ctx.send(f"Found user: {user.mention}, {user.name} (ID: {user.id})")
    else:
        await ctx.send("No user found with that ID in this server.")



@bot.event
async def on_member_join(member):
    # Sends welcome message in channel
    '''channel = discord.utils.get(member.guild.text_channels, name="bot-test")
    if channel:
        await channel.send(f"{member.mention} has joined the server!")'''

    # Prepares data payload
    payload = {
        "user_id": str(member.id),
        "user_name": f"{member.name}",
        "status": True  # True means user is in the server
    }

    # Send data to your Django backend
    async with aiohttp.ClientSession() as session:
        async with session.post("https://discord-bot-logger-backend.onrender.com/api/sync-user/", json=payload) as response:
            if response.status == 200:
                print(f"Synced {member.name} to backend.")
            else:
                print(f"Failed to sync {member.name}, status code: {response.status}")

@bot.event
async def on_member_remove(member):

    payload = {
        "user_id": str(member.id),
        "user_name": f"{member.name}",
        "status": False  # True means user is in the server
    }

    # Send data to Django backend
    async with aiohttp.ClientSession() as session:
        async with session.post("https://discord-bot-logger-backend.onrender.com/api/sync-user/", json=payload) as response:
            if response.status == 200:
                print(f"Synced {member.name} to backend.")
            else:
                print(f"Failed to sync {member.name}, status code: {response.status}")
        

@bot.command(name="list_members")
async def list_members(ctx):
    allowed_user_id = 340840136264777728 # Replace with user ID

    if ctx.author.id != allowed_user_id:
        await ctx.send("You are not authorized to use this command.")
        return

    # Ask for confirmation
    confirm_message = await ctx.send(
        f"{ctx.author.mention}, are you sure you want to get the list of all members (excluding bots)? React with ✅ to confirm or ❌ to cancel."
    )

    await confirm_message.add_reaction("✅")
    await confirm_message.add_reaction("❌")

    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) in ["✅", "❌"]
            and reaction.message.id == confirm_message.id
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)

        if str(reaction.emoji) == "✅":
            # Proceed with member listing (no join dates)
            members = [m for m in ctx.guild.members if not m.bot]
            if not members:
                return await ctx.send("No human members found.")

            payload = []
            for m in members:
                payload.append({
                    "user_id": str(m.id),
                    "user_name": f"{m.name}",
                    "status": True
                })


            async with aiohttp.ClientSession() as session:
                async with session.post("https://discord-bot-logger-backend.onrender.com/api/bulk-sync/", json=payload) as response:
                    if response.status == 200:
                        await ctx.send("All members synced to backend.")
                    else:
                        await ctx.send(f"Sync failed. Status code: {response.status}")

        else:
            await ctx.send("Command canceled.")

    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Command canceled.")

@bot.command(name="help_angela")
async def help_command(ctx):
    commands_list = [
        "`!hello_angela` - Say hello to Angela ",
        "`!angela_find_user <user_id>` - Search for a user by their Discord ID ",
        "`!list_members` - Sync and list all human members in the server",
        "`!help_angela` - Display this help message "
    ]
    
    help_text = "** Angela's Command List:**\n" + "\n".join(commands_list)
    await ctx.send(help_text)



bot.run(TOKEN)
