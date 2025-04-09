# **Snip Dis**
## Web clipping for Discord Forums

**SnipDis** is a utility Discord bot for clipping websites, articles, videos, & other web media to post to Discord Forum Channels. 
SnipDis simplifies content sharing & enables all the same features you'd have manually posting to forums, as well as tools to manage
the forums you **_snip_** to.



This command creates a thread in the specified forum channel with the provided URL and title.

---

## **Setup Instructions**  

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/yourusername/snip-dis.git
   cd snip-dis
   ```  

2. **Install dependencies**:  
   Ensure Python 3.8+ is installed, then run:  
   ```bash
   pip install -r requirements.txt
   ```  

3. **Configure the bot**:  
   Create a `.env` file and add your Discord bot token:  
   ```  
   BOT_TOKEN=your_discord_bot_token  
   ```  

4. **Run the bot**:  
   ```bash
   python main.py
   ```  

---

## **Commands**  

- **/snip**: Fetch content from a URL and create a thread in a Discord Forum Channel.  
  ```  
  /snip <url> <forum_channel> [title]  
  ```  
- **/set_nickname**: Modify the bot's nickname in the server.  
  ```  
  /set_nickname <nickname>  
  ```  
- **/set_avatar**: Change the bot's avatar using a provided image URL.  
  ```  
  /set_avatar <avatar_url>  
  ```

---

## **Permissions**  

To allow the bot to function properly, grant it the following permissions:  

- Manage Threads  
- Send Messages  
- Embed Links  
- Change Nickname (optional for customization)  

Ensure the bot is added to the correct channels with sufficient permissions.

---

## **Error Handling**  

- **Invalid URL**: Ensure the URL is correctly formatted and valid.  
- **Permission Denied**: Verify the bot has the appropriate permissions in the target forum channel.  
- **Metadata Fetch Failure**: Provide a manual title if the page does not include metadata.  
- **Missing Bot Token**: Ensure that the bot token is added to the `.env` file.  

---

## **Dependencies**  

- **discord.py**: For interacting with the Discord API.  
- **requests**: For processing web requests.  
- **BeautifulSoup**: For parsing webpage metadata.  
- **dotenv**: To manage environment variables securely.  

---

## **Contributing**  

1. Fork the repository.  
2. Clone your fork locally.  
3. Create a new branch:  
   ```bash
   git checkout -b feature-branch-name  
   ```  
4. Push your changes and submit a pull request.  

Review the contribution guidelines in the repository before submitting.  

---

## **License**  

This project is licensed under the MIT License. See the `LICENSE` file for more details.

--- 

## **Acknowledgments**  

Built using Python and py-cord to simplify and enhance content-sharing workflows in Discord forums.
