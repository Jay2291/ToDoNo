# from telebot import types
# import telebot
from credentials import bot_token, bot_api_hash, bot_api_id
from app import nearby_tasks, add_task, show_tasks, done, on_completion, del_task
import time
from telethon import events
# from telegram import Update, Bot
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from asyncio.log import logger
from telethon import TelegramClient, events ,types
import asyncio
from telethon.tl.types import MessageMediaGeoLive, PeerUser, InputGeoPoint
from telethon.tl.custom import Button
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

client = TelegramClient('session_name', bot_api_id, bot_api_hash).start(bot_token=bot_token)

# bot = telebot.TeleBot(bot_token, parse_mode='None')

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello! Type /help for instructions and enable your live location.')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_message = (
        "/key - Use custom keyboard.\n"
        "Add Task - Create your to-do list.\n"
        "Show To-Do List - Check tasks in the list.\n"
        "Delete Task - Delete tasks from the list.\n"
        "Start Search - Search for tasks to do in your vicinity.\n"
        "Close - Terminate search for tasks."
    )
    await event.respond(help_message)


@client.on(events.NewMessage(pattern='/key'))
async def key_handler(event):
    # Create the keyboard
    keyboard = [
        [Button.text('Start Search')],
        [Button.text('Show To-Do List')],
        [Button.text('Add Task')],
        [Button.text('Delete Task')],
        [Button.text('Close')]
    ]
    
    # Send the message with the keyboard
    await event.respond('Choose an option:', buttons=keyboard)

@client.on(events.NewMessage)
async def handle_response(event):
    user_id = event.peer_id.user_id
    if  event.message.text.lower() == 'show to-do list':
        await event.respond("Your to-do list:")
        tasks = show_tasks(user_id)
        i=0
        mark = '✅'
        unmark = '☐'
        for task in tasks:
            task_name , status = task
            logger.info(f" {task_name} starting")
            i+=1
            if status==1:
                await client.send_message(user_id, f"{mark}{ i}. {task_name}")
            else:
                await client.send_message(user_id, f"{unmark}{ i}. {task_name}")
    if event.message.text.lower() == 'add task':
        async with client.conversation(user_id) as conv:
            await conv.send_message("Enter the task:")
            task_response = await conv.get_response()
            oto =  task_response.text
            logger.info(f"{oto} added")
            await conv.send_message("Enter the location:")
            category_response = await conv.get_response()
            cato =  category_response.text.lower()
            logger.info(f"{cato} added")
            await conv.send_message("Enter priority for the task from 1(low) to 3(high):")
            pri_response = await conv.get_response()
            prio = pri_response.text.strip()
            logger.info(f"Priority set to {prio}. Task added successfully!")
            if oto and cato and prio:
                prio = int(prio)
                add_task(oto, cato, prio, user_id)
                await client.send_message(user_id, "Task added successfully!")
    if event.message.text.lower() == 'delete task':
        async with client.conversation(user_id) as conv:
            await conv.send_message("Enter the task name to delete:")
            task_response = await conv.get_response()
            dele =  task_response.text
            logger.info(f"{dele} deleted")
            del_task(dele)
            await client.send_message(user_id, "Task deleted successfully!")            



@client.on(events.NewMessage(pattern='Close'))
async def handle_close_command(event):
    global is_active
    is_active = False
    await event.respond("Searching Ended")

@client.on(events.NewMessage(pattern='Start Search'))
async def handle_close_command(event):
    global is_active
    global radius
    user_id = event.peer_id.user_id
    async with client.conversation(user_id) as conv:
        await conv.send_message("Enter a custom radius (in meters) or enter zero for default:")
        handle_response = await conv.get_response()
        radius = handle_response.text
        is_active = True
    await event.respond("Searching started...")

is_active = False
radius = 0
new_lat, new_lon = 0, 0

@client.on(events.MessageEdited)
async def handle_message(event):
    message = event.message
    user_id = event.peer_id.user_id
    global is_active
    global radius
    global new_lat, new_lon
    if not is_active:
        return
    if is_active:
        radius = int(radius)
        logger.info(f"Task {MessageMediaGeoLive} starting")
        if isinstance(message.media, MessageMediaGeoLive):
            location_id = message.id
            live_location = message.media.geo
            lat, lon = live_location.lat, live_location.long
                        
            com = on_completion(user_id) 
            if com:
                await client.send_message(user_id, "Congratulations! All your tasks are completed.")
                is_active = False
                await event.respond("Searching Ended")
            lat, lon = (round(lat, 6), round(lon, 6))
            print(f"Live location updated:{location_id} Latitude: {lat}, Longitude: {lon}")
            
            if new_lat != lat and new_lon != lon:
                logger.info(f"Live location updated: newlat:{new_lat}, lon:{new_lon}")
                new_lat, new_lon = lat, lon
                
                tasks = nearby_tasks(user_id, new_lat, new_lon, radius)
                if tasks:
                    for task in tasks:
                        task_info, add, task_lat, task_lon = task 
                        add_list = add.split(',')[:-3]
                        logger.info(f"Task {task[0][0]} starting")
                        await client.send_message(user_id,f"Task found:\n  1. Item: {task_info[0][0]}\n  2. Address: {' | '.join(add_list)}")
                        geoPoint = types.InputGeoPoint(task_lat, task_lon)
                        async with client.action(user_id, 'location') as action:
                            await client.send_file(user_id, types.InputMediaGeoPoint(geoPoint))
                        await asyncio.sleep(30)
                        async with client.conversation(user_id) as conv:
                            await conv.send_message("Is the task done, Y / N ?")
                            handle_response = await conv.get_response()
                            is_done = handle_response.text.lower()
                            if is_done == "y":
                                await client.send_message(message.sender_id, f"Good Job! Task {task_info[0][0]} marked as done.")
                                done(task_info[0][0])  
                            elif is_done == "n":
                                await client.send_message(message.sender_id, "Task has been snooze. Please check later.")
                                
                            else:
                                await client.send_message(message.sender_id, "Invalid response. Please reply with 'Y' or 'N'.")
                    # await client.disconnect()    
                else:
                    logger.info(f" No task present in the radius given at the moment")
            else:
                logger.info(f"User has not moved yet")
# bot.infinity_polling()
# loop = asyncio.get_event_loop
client.start()
client.run_until_disconnected()
# loop.run_forever()

