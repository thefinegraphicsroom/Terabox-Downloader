# 🌟 Terabox Download Assistant Bot  

Welcome to the **Terabox Download Assistant Bot** repository! This bot simplifies your experience with Terabox by providing direct download links, file details, and the ability to watch files online, all through Telegram.  

## 🚀 Features  

- **Direct Download Links**: Send a Terabox link, and the bot will provide a direct download link.  
- **File Streaming**: Watch your files online without downloading them.  
- **File Details**: Get important details like file size and name.  
- **Mini App Support**: Access Terabox through a sleek mini app interface.  
- **Broadcast Feature**: Admins can send messages to all users with ease.  
- **User Activity Tracking**: Monitor daily, weekly, monthly, and yearly active users.  
- **Channel Membership Enforcement**: Only subscribed users can use the bot.  

---

## 📋 Prerequisites  

Before running this bot, ensure you have the following:  

1. Python 3.10 or higher.  
2. MongoDB Atlas database.  
3. Telegram bot token and API credentials.  
4. A valid RapidAPI key for the Terabox API.  

---

## 🛠️ Installation  

Follow these steps to set up the bot:  

1. **Clone the repository**:  
   ```bash  
   https://github.com/HmmSmokieOfficial/Terabox-Downloader.git)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
3. **Set up environment variables**:
   ```bash
   API_ID=your_telegram_api_id  
   API_HASH=your_telegram_api_hash  
   BOT_TOKEN=your_bot_token  
   CHANNEL_USERNAME=your_channel_username  
   ADMIN_IDS=comma_separated_admin_ids  
   MONGO_URL=your_mongo_database_url  
   RAPIDAPI_KEY=your_rapidapi_key

4. **Run the bot**:
   ```bash
   python Terabox.py

## 🤖 Commands
      Command	Description	                                    
      /start	Start the bot and receive a welcome message.(Users)
      /stats	View user activity statistics. (Admins Only)
      /broadcast	Send a broadcast message to all bot users. (Admins Only)

## 💡 How It Works
     Users send a Terabox link to the bot.
     The bot processes the link using the Terabox API and responds with download links or file details.
     Admins can use additional commands for managing the bot and broadcasting messages.
      
## 📦 Key Technologies
      Pyrogram: Telegram Bot API library.
      Motor: Asynchronous MongoDB driver.
      Aiohttp: For handling API requests.
      Docker: Containerized deployment.


## 🤝 Contributing
      Contributions are welcome! Please follow these steps:
      Fork the repository.
      Create a feature branch (git checkout -b feature-name).
      Commit your changes (git commit -m 'Add some feature').
      Push to the branch (git push origin feature-name).
      Open a pull request.
   
## 📧 Support
    For support or inquiries, contact the Bot Owner [ HMM٭SMOKIE](https://t.me/hmm_Smokie).
    Happy botting! 🚀
    Let me know if you’d like to customize this further!

      




