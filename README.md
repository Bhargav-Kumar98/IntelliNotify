# IntelliNotify

**AI-Powered Discord Message Filtering & Notification System**

IntelliNotify is a smart Discord bot designed to help users filter messages based on their preferences and receive real-time notifications about relevant content. Powered by LangChain and Groq's AI APIs, it ensures accurate message relevance detection. MongoDB is used for persistent storage, allowing users to seamlessly manage their preferences across multiple servers.

---

## Key Features

- **Customizable Message Filtering**: Set personal preferences to filter out messages by topics or keywords in each Discord server.
- **AI-Driven Relevance Detection**: Leverages LangChain and Groq APIs to intelligently assess and detect relevant messages.
- **Real-Time Notifications**: Get instant alerts when messages matching your preferences are detected.
- **Admin Controls**: Includes commands for server admins to configure and manage bot behavior.
- **Persistent Data Storage**: User preferences and server data are securely stored in MongoDB.
- **User-Friendly Setup**: Easy-to-follow command interface for seamless configuration and preference management.

---

## Prerequisites

Before setting up IntelliNotify, ensure you have the following:

1. **Discord Developer Mode**: Enabled in your Discord settings (Settings > Advanced > Developer Mode).
2. **MongoDB**: A running instance of MongoDB (local or remote).
3. **Environment Variables**: Create a `.env` file with the following keys:
   - `DISCORD_TOKEN`: Your Discord bot token.
   - `GROQ_API_KEY`: Your Groq API key.

---

## Setup Instructions

To set up IntelliNotify, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/intellinotify.git
   cd intellinotify
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create the `.env` File**:
   Add your credentials to a `.env` file as follows:
   ```env
   DISCORD_TOKEN=your_discord_token
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Create the `user_data.json` File**:
   Include user ID and preferences in the `user_data.json` file:
   ```json

   {
        "_id": 8901234567890123456,
        "servers": [
            {
                "server_name": "Tech Enthusiasts",
                "preferences": [
                    "Notify me about AI and machine learning discussions.",
                    "Let me know if someone shares interesting programming tutorials.",
                    "Alert me if any tech events are being organized."
                ]
            },
            {
                "server_name": "Gaming Legends",
                "preferences": [
                    "Notify me about multiplayer game updates.",
                    "Let me know if there are any new game releases.",
                    "Alert me when a gaming tournament is announced."
                ]
            }
        ]
    },
    {
        "_id": 4567890123456789012,
        "servers": [
            {
                "server_name": "Travel Buffs",
                "preferences": [
                    "Let me know if someone shares unique travel destinations.",
                    "Notify me about group travel opportunities.",
                    "Alert me about travel discounts or promotions."
                ]
            },
            {
                "server_name": "Foodies Unite",
                "preferences": [
                    "Notify me about new restaurant openings.",
                    "Let me know if there are food festivals happening.",
                    "Alert me about cooking challenges or recipes."
                ]
            }
        ]
    }

   ```

5. **Initialize the Database**:
   Set up MongoDB by running the following command:
   ```bash
   python database.py
   ```

6. **Start the Bot**:
   Launch IntelliNotify with:
   ```bash
   python main.py
   ```

---

## Commands

### User Commands

- `!ping`: Check if the bot is online and responsive.
- `!add_preference <preference>`: Add a preference to filter messages.
- `!remove_preference <preference>`: Remove a specific preference.
- `!view_preferences`: View your current message preferences.
- `!reset_preferences`: Clear all preferences for the current server.

### Admin Commands

- `!authorize_user <user_id>`: Grant a user access to the bot.
- `!deauthorize_user <user_id>`: Revoke a user's access.
- `!view_authorized_users`: List all users authorized to use the bot.

---

## How It Works

1. **User Authorization**:
   - When the bot starts, it checks MongoDB for authorized users.
   - The bot owner is automatically authorized if no other users are set.

2. **Message Monitoring**:
   - Continuously scans and processes messages in connected servers.
   - Utilizes LangChain and Groq APIs to evaluate if messages match user preferences.

3. **Real-Time Notifications**:
   - Sends immediate alerts to users when relevant messages are found.
   - Notifications are customized to match user-specific preferences.

4. **Preference Management**:
   - Users can easily add, remove, view, or reset preferences via simple commands.
   - All preferences are securely stored and synced with MongoDB for persistence.

---

## File Structure

- `main.py`: Main bot script containing core functionalities.
- `database.py`: Script for initializing and managing the MongoDB database.
- `.env`: Environment variables (this file is excluded from version control).
- `requirements.txt`: List of required Python packages for the bot.
- `README.md`: Documentation for the project.

---

## Dependencies

- `discord.py`: Framework for building the Discord bot.
- `pymongo`: MongoDB integration for storing data.
- `python-dotenv`: Manage environment variables.
- `langchain`: Used for AI-driven message relevance detection.
- `asyncio`: For asynchronous operations in the bot.

Install all dependencies with:
```bash
pip install -r requirements.txt
```

---

## Future Enhancements

- **Auto-Reply Capabilities**: Implement automatic responses or suggestions based on message relevance.
- **Enhanced AI Models**: Integrate additional AI models to further improve message relevance accuracy.
- **Scalability**: Migrate to cloud-hosted MongoDB and support multiple server environments.

---

**Happy Messaging with IntelliNotify!** 🚀

--- 
