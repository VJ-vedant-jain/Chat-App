# Chat-App
A simple chatapp build on python with socket and gui on pyqt5 (to be changed to pyqt5 when all gui stuff handled)

Old versions saved in folder named "previous versions"

# Requirements

You must have mySQL v.8 or higher installed on your system, and have configured your root user with a password. Simply follow Oracle's documentation.

The server file will automagically generate the database for you

# Changelog V4.4.0.test

Uploaded on 23 April, 2025.

Changes - 
1. Added a whole ass gui for the server (/src/ui/server)
2. Removed some unnecessary checks for stuff

# Current Server Admin Commands

1. /kick "username" - obvious
2. /abort - exits the server immediately, disconnecting all clients.
3. /clear-all - clears the entire message history/SQL database. Slightly destructive, use with caution.
4. /prune - clears the last set amount of messages. Run the command, then the server will ask you for a number of messages.
5. /ban "username" - obvious

More functions will be coming soon :)

# Known Issues

1. CLI version is.... a work in progress. Ignore it.
2. .ui and .py files have a bit a difference in gui. (.py ahead of .ui), needs to be merged

# Future Plan

1. Replace the label showing current server with a dropdown showing active servers (oh boii this gon be lit) 
2. Add certain "channels" or "sub chats" within servers, allowing for organized conversations. (yea this will be... hard af)
3. Add a ban list to ban or restrict a user. This includes muted users, restricted access to channels, and the fun banhammer.
    **planning to have banned user list being saved to a file**