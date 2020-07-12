import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import asyncio
import itertools
import copy



ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/cache/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

#ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, guildId = None):
        ytdl_custom = ytdl_format_options
        ytdl_custom['outtmpl'] = '/cache/'+str(guildId)+'.mp3'
        ytdl = youtube_dl.YoutubeDL(ytdl_custom)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Playlist:

    def __init__(self, name, desc, folder):
        self.name = name
        self.desc = desc
        self.files = itertools.cycle([folder+'/'+path for path in os.listdir(folder) if path.endswith('.mp3')])

class PlaylistList(list):

    def __init__(self, path):
        with open(os.path.join(path,'dict.txt'),'r') as playlists:
            lines = playlists.readlines()
            for playlist in lines:
                name, desc, folder = playlist.split('|')
                folder = path+'/'+folder[:-1]
                self.append(Playlist(name, desc, folder))

class Player(commands.Cog):
    '''Модуль плеера для Tsubasa-radio.'''

    def __init__(self, client):
        self.playlists = PlaylistList('./songs')
        self.cyclesOfGuilds = dict()
        self.client = client


    def removeMusic(self, ctx, loop):
        '''
        loopCurr = loop or asyncio.get_event_loop()
        asyncio.set_event_loop(loopCurr)
        loopCurr.run_until_complete(zaWarudo())
        '''
        zaWarudo = asyncio.sleep(0.5)
        fut = asyncio.run_coroutine_threadsafe(zaWarudo, loop)
        fut.result()
        '''
        voice = get(self.client.voice_clients, guild = ctx.guild)
        print('PLAYING:',voice.is_playing())
        print(str(ctx.guild.id))
        '''
        try:
            os.remove('./cache/'+str(ctx.guild.id)+'.mp3')
        except:
            print('fail NA')

    def updateTrack(self, ctx, trackCycle):
        voice = get(self.client.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected() and ctx.guild.id in self.cyclesOfGuilds:
            voice.play(discord.FFmpegPCMAudio(next(trackCycle)), after = lambda err: self.updateTrack(ctx, trackCycle))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

    def removePlaylistMusic(self, ctx):
        if self.cyclesOfGuilds.get(ctx.guild.id, False):
            del self.cyclesOfGuilds[ctx.guild.id]


    '''
    def removeMusicNoSleep(self, ctx):
        print(str(ctx.guild.id),'A')
        try:
            os.remove('./cache/'+str(ctx.guild.id)+'.mp3')
        except:
            print('fail A')
    '''
    

    @commands.Cog.listener()
    async def on_ready(self):
        print('player is ready')

    @commands.command(aliases = ['j',])
    async def join(self, ctx, *, channel : discord.VoiceChannel):
        """
        Заходит на указанный канал. Пример: !j GUCCI gang
        """
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and voice.is_connected():
            print('conn')
            self.removePlaylistMusic(ctx)
            await ctx.voice_client.move_to(channel)         #если на другом канале
        else:
            await channel.connect()                         #если ни на одном

    @commands.command(aliases = ['l',])
    async def leave(self, ctx):
        """
        Выходит с канала
        """
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and voice.is_connected():
            self.removePlaylistMusic(ctx)
            await voice.disconnect()

    @commands.command(aliases = ['pp',])
    async def playplaylist(self, ctx, numOfPlaylist):
        '''
        Играет музыку из плейлиста. Передайте номер. Пример: !pp 0
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected():
            if voice.is_playing() or voice.is_paused():
                    self.removePlaylistMusic(ctx)
                    voice.stop()
            await asyncio.sleep(0.5)
            self.cyclesOfGuilds[ctx.guild.id] = copy.deepcopy(self.playlists[int(numOfPlaylist)].files)
            trackCycle = self.cyclesOfGuilds[ctx.guild.id]
            voice.play(discord.FFmpegPCMAudio(next(self.cyclesOfGuilds[ctx.guild.id])), after = lambda err: self.updateTrack(ctx, trackCycle))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07
        
    @commands.command(aliases = ['n',])
    async def next(self, ctx):
        '''
        Переходит на следующий трек в плейлисте.
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)
        if voice and (voice.is_playing() or voice.is_paused()) and ctx.guild.id in self.cyclesOfGuilds:
            voice.stop()

        

    @commands.command(aliases = ['pi',])
    async def playinternet(self, ctx, *, url):
        '''
        Играет музыку из интернета. Передайте url. Пример: !pi url
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected():
            async with ctx.typing():
                
                if voice.is_playing() or voice.is_paused():
                    self.removePlaylistMusic(ctx)
                    voice.stop()
                
                '''
                #await asyncio.sleep(0.5)
                #self.removeMusicNoSleep(ctx)

                filename = str(ctx.guild.id)+'.mp3'
                ydl_opts = {
                        'format': 'bestaudio/best',
                        'quiet': True,
                        'outtmpl': '/cache/'+filename,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
                    ytdl.download([url])
            voice.play(discord.FFmpegPCMAudio('./cache/'+filename), after = lambda err: self.removeMusic(ctx, self.client.loop))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07
            print('playing')
            '''
            
                player = await YTDLSource.from_url(url, loop=self.client.loop, stream = False, guildId = ctx.guild.id)
            voice.play(player, after = lambda err: self.removeMusic(ctx, self.client.loop))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07
            


    @commands.command(aliases = ['p',])
    async def pause(self, ctx):
        '''
        Ставит трек на паузу.
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and voice.is_playing():
            voice.pause()

    @commands.command(aliases = ['r',])
    async def resume(self, ctx):
        '''
        Запускает трек заново.
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and voice.is_paused():
            voice.resume()

    @commands.command(aliases = ['s',])
    async def stop(self, ctx):
        '''
        Останавливает текущий трек.
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and (voice.is_paused() or voice.is_playing()):
            self.removePlaylistMusic(ctx)
            voice.stop()
            #await asyncio.sleep(0.5)
            #self.removeMusicNoSleep(ctx)

    @commands.command(aliases = ['v',])
    async def volume(self, ctx, vol):
        '''
        Установливает громкость текущего трека. Стоковая: 0.07 Пример: !vol 0.5
        '''
        await ctx.channel.purge(limit = 1)
        voice = get(self.client.voice_clients, guild = ctx.guild)

        if voice and (voice.is_paused() or voice.is_playing()):
            voice.source.volume = float(vol)

    @commands.command(aliases = ['spl',])
    async def showplaylists(self, ctx):
        '''
        Выводит доступные плейлисты.
        '''
        await ctx.channel.purge(limit = 1)
        embed = discord.Embed( title = "Доступные треклисты", colour = discord.Colour.purple())
        embed.set_image(url = "https://ih0.redbubble.net/image.261648349.8582/flat,750x1000,075,t.u5.jpg")
        embed.set_author(name = "Saiko... 多分",icon_url = "https://pm1.narvii.com/6855/731d002f57eabad1d77b609b9b4d351afc6b9684v2_hq.jpg")
        embed.set_footer(text = "!help - команды")
        for i, playlist in enumerate(self.playlists):
            embed.add_field(name = "#"+str(i)+" "+playlist.name, value = playlist.desc,inline = False)
        await ctx.send(embed = embed)


    



def setup(client):
    client.add_cog(Player(client))