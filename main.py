import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
import logging
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client['user_data']
    authorized_users_collection = db['authorized_users']
    logging.info("Connected to MongoDB successfully")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")
    exit(1)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Groq client using LangChain
groq_model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY
)

@bot.event
async def on_ready():
    try:
        logging.info(f'{bot.user} has connected to Discord!')
        logging.info(f'Bot is in {len(bot.guilds)} servers.')
        
        all_users = list(authorized_users_collection.find())
        logging.info(f"Found {len(all_users)} authorized users in the database")
        
        AUTHORIZED_USERS = [user['_id'] for user in all_users]
        
        if not AUTHORIZED_USERS:
            application = await bot.application_info()
            owner_id = application.owner.id
            AUTHORIZED_USERS.append(owner_id)
            authorized_users_collection.insert_one({"_id": owner_id, "servers": []})
            logging.info(f"Added owner with ID {owner_id} as an authorized user")
        
        for user_id in AUTHORIZED_USERS:
            try:
                user = await bot.fetch_user(user_id)
                logging.info(f"Checking for authorized user with ID: {user_id}")
                
                shared_servers = []
                for guild in bot.guilds:
                    try:
                        member = await guild.fetch_member(user_id)
                        if member:
                            shared_servers.append(guild)
                    except discord.errors.NotFound:
                        pass
                    await asyncio.sleep(0.5)
                
                logging.info(f"\nServers where both the bot and user {user.name} are present:")
                
                user_data = authorized_users_collection.find_one({"_id": user_id})
                if not user_data:
                    user_data = {"_id": user_id, "servers": []}
                
                for guild in shared_servers:
                    server_entry = next((s for s in user_data["servers"] if s["server_name"] == guild.name), None)
                    if server_entry:
                        logging.info(f"Server: {guild.name}")
                        logging.info(f"Preferences for {user.name}: {', '.join(server_entry['preferences'])}")
                        logging.info("-" * 30)
                
                authorized_users_collection.update_one({"_id": user_id}, {"$set": user_data}, upsert=True)
                
                if shared_servers:
                    logging.info(f'Server preferences checked for {len(shared_servers)} shared servers for user {user.name}.')
                else:
                    logging.info(f"There are no servers where both the bot and user {user.name} are present.")
            except Exception as e:
                logging.error(f"Error processing user {user_id}: {str(e)}")
            await asyncio.sleep(1)
        
        logging.info("on_ready event completed successfully")
    except Exception as e:
        logging.error(f"Error in on_ready event: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        all_users = authorized_users_collection.find()
        for user in all_users:
            user_id = user['_id']
            server_entry = next((s for s in user['servers'] if s['server_name'] == message.guild.name), None)
            if server_entry and server_entry['preferences']:
                user_preferences = server_entry['preferences']
                relevance = await check_relevance(message.content, user_preferences)
                if relevance:
                    discord_user = await bot.fetch_user(user_id)
                    await discord_user.send(f"New relevant post by {message.author.name} in {message.guild.name} - #{message.channel.name}:\n{message.content}")
    except Exception as e:
        logging.error(f"Error in on_message event: {str(e)}")

    await bot.process_commands(message)

async def check_relevance(content, preferences):
    preferences_str = '; '.join(preferences)
    prompt = f"Is the following message relevant based on these preferences: '{preferences_str}'? Answer with only 'Yes' or 'No'. Message: {content}"
    
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant that determines message relevance strictly based on the given preferences."),
            HumanMessage(content=prompt)
        ]
        response = groq_model.invoke(messages)
        answer = response.content.strip().lower()
        return answer == 'yes'
    except Exception as e:
        logging.error(f"Error in Groq API call: {e}")
        return False

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_permissions(administrator=True)
async def add_preference(ctx, *, new_preference):
    try:
        user_id = ctx.author.id
        user_data = authorized_users_collection.find_one({"_id": user_id})
        if not user_data:
            user_data = {"_id": user_id, "servers": []}
        
        server_entry = next((s for s in user_data["servers"] if s["server_name"] == ctx.guild.name), None)
        if not server_entry:
            server_entry = {"server_name": ctx.guild.name, "preferences": []}
            user_data["servers"].append(server_entry)
        
        server_entry["preferences"].append(new_preference)
        authorized_users_collection.update_one({"_id": user_id}, {"$set": user_data}, upsert=True)
        await ctx.send(f"New preference added for {ctx.author.name}: {new_preference}")
    except Exception as e:
        logging.error(f"Error in add_preference command: {str(e)}")
        await ctx.send("An error occurred while adding the preference.")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove_preference(ctx, *, preference):
    try:
        user_id = ctx.author.id
        user_data = authorized_users_collection.find_one({"_id": user_id})
        server_entry = next((s for s in user_data["servers"] if s["server_name"] == ctx.guild.name), None)
        if server_entry and preference in server_entry["preferences"]:
            server_entry["preferences"].remove(preference)
            authorized_users_collection.update_one({"_id": user_id}, {"$set": user_data})
            await ctx.send(f"Preference removed for {ctx.author.name}: {preference}")
        else:
            await ctx.send("Preference not found.")
    except Exception as e:
        logging.error(f"Error in remove_preference command: {str(e)}")
        await ctx.send("An error occurred while removing the preference.")

@bot.command()
async def view_preferences(ctx):
    try:
        user_id = ctx.author.id
        user_data = authorized_users_collection.find_one({"_id": user_id})
        server_entry = next((s for s in user_data["servers"] if s["server_name"] == ctx.guild.name), None)
        if server_entry and server_entry["preferences"]:
            preferences = server_entry["preferences"]
            await ctx.send(f"Current preferences for {ctx.author.name}:\n" + "\n".join(f"- {pref}" for pref in preferences))
        else:
            await ctx.send(f"No preferences set for {ctx.author.name} in this server.")
    except Exception as e:
        logging.error(f"Error in view_preferences command: {str(e)}")
        await ctx.send("An error occurred while retrieving preferences.")

@bot.command()
@commands.has_permissions(administrator=True)
async def reset_preferences(ctx):
    try:
        user_id = ctx.author.id
        user_data = authorized_users_collection.find_one({"_id": user_id})
        if user_data:
            server_entry = next((s for s in user_data["servers"] if s["server_name"] == ctx.guild.name), None)
            if server_entry:
                server_entry["preferences"] = []
                authorized_users_collection.update_one({"_id": user_id}, {"$set": user_data})
                await ctx.send(f"Preferences reset for {ctx.author.name} in this server.")
            else:
                await ctx.send("No preferences found for this server.")
        else:
            await ctx.send("No user data found.")
    except Exception as e:
        logging.error(f"Error in reset_preferences command: {str(e)}")
        await ctx.send("An error occurred while resetting preferences.")

async def main():
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logging.error(f"Error starting the bot: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
