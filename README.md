# Chat-App
A simple chatapp build on python with socket and gui on tkinter

# Requirements

You must have mySQL v.8 or higher installed on your system, and have configured your root user with a password. Simply follow Oracle's documentation.

The server file will automagically generate the database for you

# Changelog V4.3.2.test

Uploaded on 20 April, 2025.

Old versions now saved in folder named "previous versions"

Changes - 
1. Rehauled the whole UI
2. Now shows server ip and port to support different chatrooms and allows you to change server after being loaded
3. A Debug box now shows what really happened... to be improved in future updates :)
4. New Server Admin functions have been added with multithreading. The CLI will now show some commands.

# Current Server Admin Commands

1. /kick username - obvious
2. /abort - exits the server immediately, disconnecting all clients.
3. /clear-all - clears the entire message history/SQL database. Slightly destructive, use with caution.
4. /prune - clears the last set amount of messages. Run the command, then the server will ask you for a number of messages.

More functions will be coming soon :)

# Known Issues

1. DM window on the main client once closed, does not open again. Fixing it right now. - Sadly still exists
3. CLI version is.... a work in progress. Ignore it.
3. Stuff looking kinda basic, styling will be added soon. - Kindaaa fixed
4. Loaded messages have a bit of problem with usernames. Instead of [username]: you see [[username]:]:

# Future Plan

1. Replace the label showing current server with a dropdown showing active servers (oh boii this gon be lit)
2. Add a ton of more commands, heck, lets make the server itself a GUI.
3. Add certain "channels" or "sub chats" within servers, allowing for organized conversations. (yea this will be... hard af)
4. Add a ban list to ban or restrict a user. This includes muted users, restricted access to channels, and the fun banhammer.