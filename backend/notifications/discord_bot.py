import requests
from django.conf import settings

def send_discord_dm(discord_id, message):
    """Sends a direct message to a user on Discord."""
    if not settings.DISCORD_BOT_TOKEN or not discord_id:
        return # Don't try to send if the bot token or user ID is missing

    bot_token = settings.DISCORD_BOT_TOKEN
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
    }

    # Step 1: Create a DM channel with the user
    create_dm_url = "https://discord.com/api/v9/users/@me/channels"
    create_dm_payload = {"recipient_id": discord_id}

    try:
        response = requests.post(create_dm_url, headers=headers, json=create_dm_payload)
        response.raise_for_status() # Raise an exception for bad status codes
        channel_id = response.json()['id']

        # Step 2: Send the message to the created DM channel
        send_message_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        send_message_payload = {"content": message}

        send_response = requests.post(send_message_url, headers=headers, json=send_message_payload)
        send_response.raise_for_status()
        print(f"Successfully sent Discord DM to {discord_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord DM to {discord_id}: {e}")
