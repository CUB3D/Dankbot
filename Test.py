#!/usr/bin/python3.4

import discord
import asyncio
import requests
from random import choice as select
from os.path import isfile

token = ""
commands = []
admin_name = ""
config = {}

def onStartup():
    global token
    global config
    fileHandle = open("Token.conf")
    token = fileHandle.readline().rstrip("\n")
    fileHandle.close()
    if isfile("Settings.conf"):
        fileHandle = open("Settings.conf", "r")
        for line in fileHandle:
            elements = line.rstrip("\n").split("=")
            config[elements[0]] = elements[1]
        fileHandle.close()
    if isfile("Admin.conf"):
        fileHandle = open("Admin.conf", "r")
        global admin_name
        admin_name = fileHandle.readline().rstrip("\n")
        fileHandle.close()

def onClose():
    global config
    fileHandle = open("Settings.conf", "w")
    for key in config:
        fileHandle.write(key + "=" + config[key] + "\n")
    fileHandle.close()
    fileHandle = open("Admin.conf", "w")
    fileHandle.write(admin_name)
    fileHandle.close()

client = discord.Client()

def messageFromAdmin(message):
    global admin_name

    return admin_name == str(message.author)

@client.event
@asyncio.coroutine
def on_ready():
    print("Logged in as:", client.user.name, "with id:", client.user.id)
    print("Hello, humans")

@client.event
@asyncio.coroutine
def on_message(message):
    print("Got message:", message.content)

    global commands

    for command in commands:
        if message.content.startswith(command['command']):
            print("Running callback")
            return command['callback'](message)


def register_function(command, callback):
    command = {
        "command":command,
        "callback": callback
    }

    global commands

    commands.append(command)

def kill_callback(message):
    if messageFromAdmin(message):
        yield from client.send_message(message.channel, "killing client")
        onClose()
        client.close()
        exit()
    else:
        yield from client.send_message(message.channel, "Permission Denied")

@asyncio.coroutine
def ping_callback(message):
    print("Sending pong responce")
    yield from client.send_message(message.channel, "pong")

def meme_callback(message):
    tmp = yield from client.send_message(message.channel, "Getting memes")

    headerData = {
        'User-Agent': "Part of a discord bot",
        "From": "CUB3D"
    }

    redditResponce = requests.get("http://reddit.com/r/dankmemes/hot.json", headerData)
    json = redditResponce.json()
    if "error" in json:
        if int(json["error"]) == 429:
            print("Too many requests")
            yield from client.edit_message(tmp, "Error: Too dank, much request (try again later)")
            return

    children = json["data"]["children"]
    selected = select(children)
    url = selected["data"]["url"]

    print("Image URL:", url)

    yield from client.edit_message(tmp, str(url))

def repeat_callback(message):
    split = message.content.split("=")
    msg = split[1].replace("\\n", "\n")
    count = int(split[2])
    if "maxCount" in config:
        count = min(count, int(config["maxCount"]))
    print("Printing '" + msg + "'",  str(count), "times")
    for i in range(0, count):
        yield from client.send_message(message.channel, msg)

def setAdmin(message):
    global admin_name
    adminName = message.author
    print(str(adminName), "is trying to become admin")
    if input("Type ok to accept: ") == "ok":
        print("Accepted")
        admin_name = str(adminName)
    else:
        print("Denied")

def setConfig(message):
    if messageFromAdmin(message):
        split = message.content.split("=")
        config[split[1]] = split[2]
        yield from client.send_message(message.channel, "Config updated")
    else:
        yield from client.send_message(message.channel, "Permission Denied")

def nicememe_callback(message):
    yield from client.edit_message(message, "http://niceme.me")

def help_callback(message):
    global commands
    output = "Commands: "

    for command in commands:
        output += command['command'] + ", "

    output = output.rstrip(", ")

    yield from client.send_message(message.channel, output)

register_function(":meme", meme_callback)
register_function(":ping", ping_callback)
register_function(":kill", kill_callback)
register_function(":wq", kill_callback)
register_function(":rep", repeat_callback)
register_function(":adm", setAdmin)
register_function(":nice", nicememe_callback)
register_function(":help", help_callback)
register_function(":conf", setConfig)

onStartup()
client.run(token)
