import requests
from django.conf import settings

def send_discord_dm(discord_id, message):
    """
    Send a direct message to a user via Discord bot.
    :param discord_id: The user's Discord user ID (as a string)
    :param message: The message to send
    :return: True if sent, False otherwise
    """
    # Step 1: Create a DM channel
    url = 'https://discord.com/api/v10/users/@me/channels'
    headers = {
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {"recipient_id": str(discord_id)}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        return False
    channel_id = resp.json().get('id')
    if not channel_id:
        return False
    # Step 2: Send the message
    msg_url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    msg_data = {"content": message}
    msg_resp = requests.post(msg_url, headers=headers, json=msg_data)
    return msg_resp.status_code == 200
