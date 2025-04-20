# Chat-App
A simple chatapp build on python with socket and gui on tkinter

# Requirements

You must have mySQL v.8 or higher installed on your system, and have configured your root user with a password. Simply follow Oracle's documentation.

The server file will automagically generate the database for you

# Changelog V4.3.3.test

Uploaded on 20 April, 2025.

Old versions now saved in folder named "previous versions"

Changes - 
1. Fixed the error of DM windows being unable to be opened after one of close
2. Fixed usernames of loading chat history being [[user]:]: and not [user]:
3. Fixed error of debug box and log_server.txt being spammed by "Message sent"
4. Added a feature to ban users from server

# Current Server Admin Commands

1. /kick "username" - obvious
2. /abort - exits the server immediately, disconnecting all clients.
3. /clear-all - clears the entire message history/SQL database. Slightly destructive, use with caution.
4. /prune - clears the last set amount of messages. Run the command, then the server will ask you for a number of messages.
5. /ban "username" - obvious

More functions will be coming soon :)

# Known Issues

1. DM window on the main client once closed, does not open again. Fixing it right now. - Sadly still exists
    **FIXED**
3. CLI version is.... a work in progress. Ignore it.
3. Stuff looking kinda basic, styling will be added soon. - Kindaaa fixed
4. Loaded messages have a bit of problem with usernames. Instead of [username]: you see [[username]:]:
    **FIXED AFTER IMPLEMENTING CHECKS IN 3 PLACES AHHHHHHH (Rudy you might need to see if there is a better way)**
5. Error of debug box in client and log_server.txt being spammed by "Message sent"
    **FIXED**

# Future Plan

1. Replace the label showing current server with a dropdown showing active servers (oh boii this gon be lit)
2. Add a ton of more commands, heck, lets make the server itself a GUI.
3. Add certain "channels" or "sub chats" within servers, allowing for organized conversations. (yea this will be... hard af)
4. Add a ban list to ban or restrict a user. This includes muted users, restricted access to channels, and the fun banhammer.
    **ADDED BUT NEEDS SOME... CHANGES. planning to have banned user list being saved to a file**