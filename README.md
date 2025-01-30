# 🌐✨ **Snip Dis** – A Web Snipper for Discord Forums 👾💬
Welcome to **Snip Dis**, your powerful companion for easily sharing web content to Discord forums! **Snip Dis** fetches webpage titles, validates links, and organizes information into beautifully threaded forum posts, bringing seamless content sharing directly to your Discord servers.
## 🎯 **Features**
- 🔗 **Fetch & Share Titles**: Automatically extract a webpage's title from a URL and create detailed threads in Discord forums.
- 📝 **Custom Titles**: Can't extract the title? No problem! Provide a manual title for accurate content threads.
- 📜 **Beautiful Embeds**: Automatically create and format stunning embeds for more professional and eye-catching posts.
- ⚙️ **Easy Admin Configurations**:
    - Set bot nicknames for improved server management.
    - Update bot avatars dynamically using URLs for a customizable experience.

- 🛡️ **Validation & Error Handling**:
    - Automatically validates URLs for syntax issues.
    - Provides meaningful error feedback to users on invalid links or bot permission limitations.

- 🤖 **Effortless Integration**: With Slash commands designed for simplicity, you can take full control over your forum-sharing needs.

## 🛠️ **Installation**
To set up **Snip Dis**, follow these steps:
### 1. Clone the Repository
``` bash
git clone https://github.com/yourusername/snip-dis.git
cd snip-dis
```
### 2. Install Dependencies
Ensure you have Python 3.8+ installed:
``` bash
pip install -r requirements.txt
```
### 3. Add Your Discord Bot Token
Set up a `.env` file in the project root:
``` 
BOT_TOKEN=your_discord_bot_token_here
```
🔑 Need to create a bot? Follow [this guide]() to get your token and set up OAuth scopes for **applications.commands** and **bot**.
### 4. Run the Bot
``` bash
python main.py
```
Your bot, **Snip Dis**, is now live! 🎉
## 🖇️ **Available Commands**
### 1. **/snip**

> _Fetch a URL's title and create a forum thread._
> 

- **Usage**: `/snip <url: str> [channel: ForumChannel] [title: str]`
- **Example**:
`/snip url=https://example.com channel=#web-links`
📜 Create a thread containing the page's metadata in the specified forum channel.

### 2. **/set_nickname**

> _Set the bot's nickname in the current server._
> 

- **Usage**: `/set_nickname <nickname: str>`
- **Example**:
`/set_nickname SnipBot`
🤖 Rename the bot to "SnipBot" in your Discord server.

### 3. **/set_avatar**

> _Update the bot's avatar dynamically using an image URL._
> 

- **Usage**: `/set_avatar <avatar_url: str>`
- **Example**:
`/set_avatar https://example.com/my-avatar.png`
🌟 Give your bot a fresh look with a custom avatar image.

## ⚙️ **Configuration**
### Bot Permissions
Minimum bot permissions required:
- `Manage Threads`
- `Send Messages`
- `Embed Links`
- `Change Nickname` (Optional)

Ensure the bot has access to the specific forum channels where it needs to operate.
### Dependencies
The bot uses the following:
- **[discord.py]()**: For interacting with the Discord API.
- **[requests]()**: For retrieving webpage data.
- **[BeautifulSoup]()**: For parsing webpage metadata.
- **[Python-dotenv]()**: For easy environment variable management.

## ❗ **Error Handling**

| Error | Cause | Solution |
| --- | --- | --- |
| `Invalid URL provided` | URL does not conform to standard formatting. | Check the URL syntax before providing it to the bot. |
| `Permission Error` | Bot lacks permissions to create threads in forums. | Ensure the bot has the necessary permissions in the forum channel. |
| `Title extraction failure` | The webpage has no `<title>` tag, or content is dynamic (e.g., JavaScript-rendered). | Provide a manual `title` argument when using `/snip`. |
| `Bot token missing` | BOT_TOKEN not set in `.env`. | Add your bot token to the `.env` file as shown in the setup steps. |

Feel free to suggest features or report bugs via [Issues]().
## 🤝 **Contributing**
We welcome contributions! To get started:
1. Fork the repository.
2. Clone it locally.
3. Branch from `main`: `git checkout -b feature-name`.
4. Push your changes: `git push origin feature-name`.
5. Open a Pull Request.

Be sure to follow the **[contributor guidelines]()**.
## 📜 **License**
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it, but make sure to credit the original authors. See the full license in the `LICENSE` file.
## ❤️ **Acknowledgements**
- Built with 💙 using **py-cord** and **Python**.
- Inspired by the need for a streamlined way of sharing links in resource oriented Discord forum channels.

Start snipping with **Snip Dis** today and make Discord forums smarter, sleeker, and more efficient! 🚀
