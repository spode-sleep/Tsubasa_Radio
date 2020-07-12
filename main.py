import discord
from discord.ext import commands
import random
import os

TOKEN = None
STATUS = '!help-ком., !spl-муз.'
client = commands.Bot(command_prefix = '!')
client.remove_command('help')

@client.event
async def on_ready():
    print('bot is ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=STATUS))

@client.event
async def on_member_join(member : discord.Member):
    for chan in member.guild.channels:
        if isinstance(chan, discord.TextChannel):
            await chan.send('今日は, '+member.name+'さん!')
            break
    

@client.command()
@discord.ext.commands.has_permissions(administrator=True)
async def clear(ctx, n = 10):
    """Удаляет n сообщений. Доступна только админам. Пример: !clear 100"""
    await ctx.channel.purge(limit = 1)
    await ctx.channel.purge(limit = n)

@client.command(hidden = True)
async def sleep(ctx):
    '''
    Отключает бота. Только для дебага.
    '''
    await ctx.channel.purge(limit = 1)
    if ctx.message.author.id == 263943803126284300:
        await client.logout()

@client.command(aliases = ['po',])
async def ponasenkov(ctx, *, name : discord.Member):
    '''
    Ты дешёвка или букашка? Пример: !po username#0000
    '''
    await ctx.channel.purge(limit = 1)
    rand = random.randint(0,1)
    await ctx.send(name.name +' - ' + ('букашка. https://www.youtube.com/watch?v=KL3bGPGlR5o' if rand else 'дешёвка. https://www.youtube.com/watch?v=k-LPLazY22I'))


@client.command()
@discord.ext.commands.has_permissions(add_reactions=True,embed_links=True)
async def help(ctx):
    """Эта команда."""
    await ctx.channel.purge(limit = 1)
    '''
    if not cog:
            halp=discord.Embed(title='Список модулей и общих команд',
                               description='Напишите `!help модуль` чтобы узнать команды модуля (можно прямо в сообжениях).')
            cogs_desc = ''
            for x in client.cogs:
                cogs_desc += ('{} - {}'.format(x,client.cogs[x].__doc__)+'\n')
            halp.add_field(name='Модули',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
            halp.add_field(name='Команды', value = '---------------')
            for command in client.commands:
                if not command.cog_name and not command.hidden:
                    halp.add_field(name=command.name,value=str(command.help)+(('\nАльт.: '+' '.join(command.aliases)) if len(command.aliases) else ''),inline=False)
            #await ctx.message.add_reaction(emoji='✉')
            await ctx.send('',embed=halp)
    else:
            if cog in client.cogs:
                halp=discord.Embed(title='Команды '+cog, description=client.cogs[cog].__doc__)
                for command in client.get_cog(cog).get_commands():
                    if not command.hidden:
                        halp.add_field(name=command.name,value=command.help+(('\nАльт.: '+' '.join(command.aliases)) if len(command.aliases) else ''),inline=False)
                #await ctx.message.add_reaction(emoji='✉')
            else:
                #await ctx.message.add_reaction(emoji='🦄')
                halp = discord.Embed(title='Ошибка!',description='WTF? Нет такого модуля! Проверьте свой ввод.',color=discord.Color.red()) 
            await ctx.send('',embed=halp)
    '''
    halp=discord.Embed(title='Список модулей и команд')
    cogs_desc = ''
    for x in client.cogs:
        cogs_desc += ('{} - {}'.format(x,client.cogs[x].__doc__)+'\n')
    halp.add_field(name='Модули',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
    halp.add_field(name='Команды', value = 'Все команды начинаются с !. Альт. - альтернативные сокращённые названия команд.')
    for command in client.commands:
        if not command.hidden:
            halp.add_field(name=command.name,value=str(command.help)+(('\nАльт.: '+' '.join(command.aliases)) if len(command.aliases) else ''),inline=False)
    #await ctx.message.add_reaction(emoji='✉')
    await ctx.send('',embed=halp)
'''
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
'''

'''
@client.command()
async def getStr(ctx, *, args):
    await ctx.send(len(args))

@client.command()
async def mulArgs(ctx, *args):
    await ctx.send(len(args))
'''

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
client.run(TOKEN)