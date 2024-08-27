import discord
import os
import re
from dotenv import load_dotenv
import logging

load_dotenv()
TOKEN = os.getenv('TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhooks = {}

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def get_webhook(self, channel):
        if isinstance(channel, discord.Thread):
            parent_channel = channel.parent
            key = f"{parent_channel.id}_{channel.id}"
        else:
            parent_channel = channel
            key = str(channel.id)

        if key not in self.webhooks:
            webhook = await parent_channel.create_webhook(name="URL Replacer")
            self.webhooks[key] = webhook
        return self.webhooks[key]

    async def on_message(self, message):
        if message.author == self.user:  # Prevent infinite loop
            return

        # Regular expression to detect YouTube URLs
        youtube_regex = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|v/|embed/|shorts/|watch/|))(\S+)'

        # Regular expression to detect Twitter/X URLs
        twitter_regex = r'(https?://(?:www\.)?(?:twitter\.com|x\.com)/\S+)'

        # Regular expression to detect Reddit URLs
        reddit_regex = r'(https?://(?:www\.|old\.|new\.)?reddit\.com/\S+)'

        # Regular expression to detect TikTok URLs
        tiktok_regex = r'(https?://(?:www\.)?tiktok\.com/\S+)'

        def replace_youtube_url(match):
            video_id = match.group(2)
            return f'https://inv.nadeko.net/{video_id}'
        
        def replace_twitter_url(match):
            tweet_path = match.group(0).split("twitter.com/")[-1] if "twitter.com" in match.group(0) else match.group(0).split("x.com/")[-1]
            return f'https://xcancel.com/{tweet_path}'

        def replace_reddit_url(match):
            reddit_path = match.group(0).split("reddit.com/")[-1]
            return f'https://libreddit.tux.pizza/{reddit_path}'
        
        def replace_tiktok_url(match):
            tiktok_path = match.group(0).split("tiktok.com/")[-1]
            return f'https://offtiktok.com/{tiktok_path}'

        new_message = re.sub(youtube_regex, replace_youtube_url, message.content)
        new_message = re.sub(twitter_regex, replace_twitter_url, new_message)
        new_message = re.sub(reddit_regex, replace_reddit_url, new_message)
        new_message = re.sub(tiktok_regex, replace_tiktok_url, new_message)
        
        if new_message != message.content:
            try:
                # Delete the original message
                await message.delete()

                # Get or create a webhook
                webhook = await self.get_webhook(message.channel)

                # Send the new message using the webhook
                if isinstance(message.channel, discord.Thread):
                    await webhook.send(new_message, thread=message.channel, username=message.author.display_name, avatar_url=message.author.avatar.url)
                else:
                    await webhook.send(new_message, username=message.author.display_name, avatar_url=message.author.avatar.url)

            except discord.HTTPException as e:
                print(f"An error occurred: {e}")

        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)