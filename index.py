# test
#import pytchat
#import asyncio
#chat = pytchat.create(video_id="YOUTUBE_LIVE_ID")
#async def main():
#    while chat.is_alive():
#        async for c in chat.get().async_items():
#            print(f"{c.datetime} [{c.author.name}]- {c.message}")
#asyncio.run(main())

import nextcord as discord
import pytchat
import asyncio
import pyopenjtalk
import numpy as np
from scipy.io import wavfile

client = discord.Client()
TOKEN = "DISCORD_TOKEN"
Running: dict = {}
Playing: dict = {}

async def ytr(liveId: str, channel: discord.VoiceChannel):
    chat = pytchat.create(video_id=liveId)
    while chat.is_alive():
        async for c in chat.get().async_items():
            #await channel.send(f"{c.author.name} - {c.message}")
            x, sr = pyopenjtalk.tts(f"{c.author.name[:10]}   {c.message}")
            wavfile.write(f"ytr_{channel.id}.wav", sr, x.astype(np.int16))
            while Playing.get(channel.id, False): #Queue?
                await asyncio.sleep(0.2)
            Playing[channel.id] = True
            channel.guild.voice_client.play(discord.FFmpegPCMAudio(f'ytr_{channel.id}.wav', pipe=False))
            while channel.guild.voice_client.is_playing():
                await asyncio.sleep(0.2)
            Playing[channel.id] = False

new_ytr_task = lambda liveId, channel: asyncio.create_task(ytr(liveId, channel))

@client.event
async def on_ready():
    print(f"Ready {client.user.display_name}#{client.user.discriminator}")

@client.event
async def on_message(message: discord.Message):
    print(message.content)
    args = message.content.split()
    if args[0] == "ytr":
        if message.channel.id in Running.keys():
            Running[message.channel.id].cancel()
            return await message.channel.send('sucsessfully cleaned up')
        if len(args) < 2:
            return await message.channel.send('no url passed')
        if len(args[1][len(args[1])-11:]) < 11:
            return await message.channel.send('wrong url')
        if message.author.voice is None:
            return await message.channel.send('pls join voice channel')
        await message.author.voice.channel.connect()
        liveId: str = args[1][len(args[1])-11:]
        Running.update({message.channel.id: new_ytr_task(liveId, message.author.voice.channel)})
        await message.channel.send('ok')

client.run(TOKEN)