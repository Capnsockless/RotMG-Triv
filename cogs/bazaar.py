import discord
import ast
import os
import json
from discord.ext import commands
import trivdata

os.chdir(os.getcwd())
bazaar_items, bazaar_descriptions = trivdata.bazaar_items, trivdata.bazaar_descriptions
bazaarkeys, bazaarvalues = list(bazaar_items.keys()), list(bazaar_items.values())

def open_json(jsonfile):
    with open(jsonfile, "r") as fp:         #load the users.json file
        return json.load(fp)        #openfunc for jsonfiles

def save_json(jsonfile, name):          #savefunc for jsonfiles
    with open(jsonfile, "w") as fp:
        json.dump(name, fp)

def add_fame(user: discord.User, newfame: int):		#add fame to users
	users = open_json("users.json")
	id = str(user.id)
	if 2200 in ast.literal_eval(users[id]["items"]):
		users[id]["fame"] = users[id]["fame"] + round(newfame*1.25)
		save_json("users.json", users)
		return round(newfame*1.25)
	else:
		users[id]["fame"] = users[id]["fame"] + round(newfame)
		save_json("users.json", users)
		return round(newfame)

def prechecker(user):		#checks user to make sure it's on user.json, if not it will be added
	users = open_json("users.json")
	id = str(user.id)
	if id not in users.keys():
		users[id] = {"fame":10, "items":"[]"}
		save_json("users.json", users)

def strip_str(text):        #function to remove punctuations spaces from string and make it lowercase
    punctuations = ''' !-;:'`"\,/_?'''
    text2 = ""
    for char in text:
       if char not in punctuations:
           text2 = text2 + char
    return text2.lower().replace("the", "")

def take_index(l1, l2):     #Function to find the index of items in a list that are available in another list
    indexi = []
    for index, item in enumerate(l1):
        if item in l2:
            indexi.append(index)
    return indexi

def helm_of_dominator(author, price):       #give discount if userhas helm of the dominator
    users = open_json("users.json")
    if 2350 in ast.literal_eval(users[str(author.id)]["items"]):
        price *= 0.95
    return round(price)

class bazaar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief = "Check how much fame you have.")
    async def fame(self, ctx):
        users = open_json("users.json")
        prechecker(ctx.author)
        if str(ctx.author.id) in users.keys():
            authorfame = users[str(ctx.author.id)]["fame"]
            await ctx.send(f"**{ctx.author.display_name}** you currently have **``{authorfame}``** fame.")
        else:
            await ctx.send("""You haven't got any fame yet, try "ppe help" and use Triv commands to earn some.""")

    @commands.command(brief = "See what items are available.")
    async def bazaar(self, ctx):
        artifacts = ""
        for item in bazaar_items:        #concatenates all the names and prices together to form a list of bazaar items
            multiplier = 29 - len(item)
            multiplier2 = 9 - len(str(bazaar_items[item]))
            artifacts = artifacts + item + (multiplier * " ") + str(bazaar_items[item]) + (multiplier2 * " ") + bazaar_descriptions[item] + " \n"
        await ctx.send(f"``` Item:                      Price:    Description: \n{artifacts}```")

    @commands.command(brief = "Buy an item from the bazaar.")
    async def buy(self, ctx, *, purchase):
        users = open_json("users.json")
        prechecker(ctx.author)
        id = str(ctx.author.id)
        purchasestr = strip_str(purchase)
        user_items = ast.literal_eval(users[id]["items"])       #turn string of list into list
        user_fame = users[id]["fame"]
        if purchasestr not in [strip_str(x) for x in bazaarkeys]:
            await ctx.send("That item doesn't exist.")
        else:                   #list of user items is bazaard as the item prices in json file
            itemindex = [strip_str(x) for x in bazaarkeys].index(purchasestr)        #get the index of the item being purchased
            price = helm_of_dominator(ctx.author, bazaarvalues[itemindex])
            if bazaarvalues[itemindex] in user_items:            #if item is already bought
                await ctx.send("You already have that item.")
            elif price > user_fame:             #if item is too expensive
                await ctx.send(f"You don't have enough fame, this item costs {bazaarvalues[itemindex]} fame.")
            else:               #item being purchased
                user_items.append(bazaarvalues[itemindex])       #new item price is appended to users item list
                users[id]["items"] = str(user_items)        #update the list back as a string of a list
                users[id]["fame"] = users[id]["fame"] - price      #take away fame
                await ctx.send("You have purchased the item.")
                save_json("users.json", users)

    @commands.command(brief = "Sell an item from your inventory.")
    async def sell(self, ctx, *, sale):
        users = open_json("users.json")
        prechecker(ctx.author)
        id = str(ctx.author.id)
        soldstr = strip_str(sale)             #stripped item to be sold
        user_items = ast.literal_eval(users[id]["items"])           #user inventory
        strippeditems = [strip_str(x) for x in bazaarkeys]       #list of stripped bazaar items
        if soldstr in strippeditems:          #if item exists
            itemindex = strippeditems.index(soldstr)        #gets index to get item's cost
            itemcost = bazaarvalues[itemindex]
            if itemcost in user_items:          #if item is inside user inventory
                user_items.remove(itemcost)     #remove the item from inventory, add half the fame in
                users[id]["items"] = str(user_items)
                users[id]["fame"] = users[id]["fame"] + int(itemcost/2)
                await ctx.send(f"You sold the item for {int(itemcost/2)} fame.")
                save_json("users.json", users)
            else:                     #if item exists but isn't in the inventory
                await ctx.send("You don't have that item in your inventory in order to sell it.")
        else:                 #if item doesn't exist at all
            await ctx.send("That item doesn't exist in the bazaar.")

    @commands.command(brief = "Check your inventory.", aliases = ["inv"])
    async def inventory(self, ctx):         #check inventory
        users = open_json("users.json")
        prechecker(ctx.author)
        id = str(ctx.author.id)
        str_itemlist = ast.literal_eval(users[id]["items"])         #get list of items the user has(they're integers)
        if len(str_itemlist) == 0:              #if inventory is empty
            await ctx.send("Your inventory is empty, try ppe buy to purchase items.")
        else:
            indexes = take_index(bazaarvalues, str_itemlist)         #take the indexes the available items inside the list of all bazaar items
            inventory = [bazaarkeys[i] for i in indexes]     #create the actual list of strings of available inventory items
            items_listed = "``, ``".join(inventory)         #create a string to be put into the message
            await ctx.send(f"You have ``{items_listed}`` in your inventory.")

    @buy.error
    async def buyerror(self, ctx, error):
        if isinstance (error, commands.MissingRequiredArgument):
            await ctx.send("""You need to specify what item you're purchasing, try "ppe bazaar" to see available items.""")


    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            raise error

def setup(bot):
    bot.add_cog(bazaar(bot))
