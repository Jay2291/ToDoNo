# ToDoNo
ToDoNo is a Telegram bot designed to enhance task management by providing location-based notifications. Users can create a to-do list and receive reminders relevant to their current physical location, thus improving productivity and ensuring timely task completion.

# Technical Details
The ToDoNo Telegram Bot utilizes several key technologies:
- Languages and Libraries: The bot is developed using Python, leveraging the Telethon library to interact with the Telegram Bot.
Telethon provides a way to interact programmatically with Telegram’s API, offering a range of functionalities from simple bot operations to complex automation tasks. 
Telethon uses sessions to manage connections. You can save sessions to files, which lets you avoid re-authentication every time you run your script.
Telethon is built on asyncio, which allows you to perform non-blocking operations. This is essential for handling multiple simultaneous tasks efficiently.

- Location Services: The Geopify Places API is a tool that enables you to query local points of interest and amenities effortlessly. You can easily search for places in a city, within a specified radius of a point, within a reachability area, or even within a bounding box.
The Places API lets you conveniently query places by category, including accommodations, shops, parking, and much more. 
Geopify Places APIs are used for obtaining and utilizing location data, enabling the bot to send location-based notifications.

- Database: A MySQL database is employed to store user data, including task details and location information.

