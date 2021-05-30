import discord
import os
import sys, traceback
import itertools
import json
from discord.ext import commands
import trivdata

os.chdir(os.getcwd())

def open_json(jsonfile):
	with open(jsonfile, "r") as fp:
		return json.load(fp)	#openfunc for jsonfiles

def save_json(jsonfile, name):	#savefunc for jsonfiles
	with open(jsonfile, "w") as fp:
		json.dump(name, fp)

def strip_str(text):		#function to remove punctuations, spaces from string and make it lowercase,
	punctuations = ''' !-;:`'".,/_?'''
	text2 = ""
	for char in text.lower():
		if char not in punctuations:
			text2 = text2 + char
	return text2

async def find_channel(guild):      #find the first usable channel for intro message
    for chnnl in guild.text_channels:
        if not chnnl.permissions_for(guild.me).send_messages:
            continue
        return chnnl

#Help command
command_dinfos = trivdata.command_dinfos

class MyHelpCommand(commands.HelpCommand):
	async def send_bot_help(self, mapping):
		embed = discord.Embed(title="Commands:", colour=0x9b59b6)	#title and purple colour
		for cog, commands in mapping.items():
			coginfo = []		#info of cog to return
			for command in commands:
				signature = self.get_command_signature(command)	#bot prefix + command + its aliases + parameters
				if not command.hidden:
					if command.brief:		#add brief description if it's avaliable
						coginfo.append(signature+"	––––	"+str(command.brief))
					else:
						coginfo.append(signature)
			cog_name = getattr(cog, "qualified_name", "Information")	#uses "Information" if cog has no name
			embed.add_field(name=cog_name, value="\n".join(coginfo), inline=False)	#adding the string of all the command infos of cog
		channel = self.get_destination()
		embed.set_footer(text="Try ppe help <command name> to get detailed information about the command.")	#ending message
		await channel.send(embed=embed)

	async def send_command_help(self, command):         #gets the full detailed info of a command
		cmd_info = command_dinfos[strip_str(str(command))]
		await self.get_destination().send(f"{cmd_info}")

intents = discord.Intents(messages=True, members=True, guilds=True, typing=False, presences=False, voice_states=True)
bot = commands.Bot(command_prefix='ppe ', case_insensitive=True, help_command=MyHelpCommand(), intents=intents)


startcogs = ["cogs.quizes", "cogs.bazaar", "cogs.miscellaneous"]     #list of cogs to load

if __name__ == '__main__':              #loading the cogs from the directory ./cogs
    for extension in startcogs:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Try "ppe help"'))
    print('online')

@bot.event
async def on_guild_join(guild):					#sends message in the first usable channel when joining a new server
	channel = await find_channel(guild)
	await channel.send("```Hi, this is DotAQuiz, a bot that allows you to learn many details of DotA you might've never known before. You can test your knowledge of the game with the quiz commands: ppe quiz | ppe blitz | ppe shopquiz | ppe audioquiz | ppe iconquiz | ppe endless (Note that most of these commands can be quite spammy so I recommed you use a channel dedicated to spam for these commands.) and you can challenge others with  ppe duel  You can use the fame you earn with these commands to buy items with | ppe buy | that can help improve some stats in these commands. Don't forget to do ppe help and ppe help [command] to see all the information that might interest you. If you find any factual mistakes, typos and want to notify us to fix it or just want to give feedback for the bot do ppe serverinvite for an invite to our server.```")

@bot.event
async def on_guild_remove(guild):       #removes server from rngfix.json if bot gets removed
    rng = open_json("rngfix.json")
    id = str(guild.id)
    if id in rng.keys():
        rng.pop(id)
        save_json("rngfix.json", rng)

@bot.command(brief = "An invite to our discord server!")
async def serverinvite(ctx):             #sends bot information and server invite link to the server
    user = bot.get_user(ctx.author.id)
    try:
        await user.send("Note that many of the questions used by this bot were written without factchecking so you might find some incorrect information, typos and grammatical errors, new patches always make some questions outdated, if you wish to report these mistakes, just want to give feedback and suggestions or wish to see updates you can do so on this discord server:  https://discord.gg/nhBvdqV ")
        await ctx.send("Info has been sent to you.")
    except Exception:
        await ctx.send("Info can't be sent to you in direct messages(Due to your account privacy settings).")

#event for wrong "ppe cmnd"
@bot.event              #ignore and raise certain errors
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("""That command doesn't exist, try "**ppe help**" to see the existing commands.""")
    elif isinstance(error, (commands.CommandOnCooldown, commands.MissingRequiredArgument, commands.BadArgument)):
        pass
    else:
        raise error


bot.run('TOKEN')
