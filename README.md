# Workbook Crossing Bot v2
Workbook Crossing Bot is a Telegram bot that can organise workbooks exchange between students. I made it for my university groupmates in order to make workbooks exchange more convinient and structured.
### What can this bot do?
1. Convert photos to pdfs (create workbooks)
2. Filter workbooks by subject and by user
3. Get, Send and Remove workbooks
### How to use it?
1. Open chat with @WorkbookCrossingBot in Telegram

![Search for bot](https://github.com/akimich11/WBCBot2/blob/images/wb1.png)

2. Press **start** button
<img src="https://raw.githubusercontent.com/akimich11/WBCBot2/images/wb2.jpg" width=391>

3. Follow the bot instructions
### User options
1. Create workbooks by sending photos to bot
2. Get workbooks by subject name and user
3. Remove own workbooks 
### Administrator options
1. Make and Remove other admins
2. Remove any user's workbooks
3. Create and Remove subjects
4. Get list of all users
5. Ban and Unban any users (even other admins)

## About v2
This is my second attempt to implement an idea of workbook exchange using Python and Telegram API. My first attempt you can see in this repository: https://github.com/akimich11/WBCBot. But there is a lot of differences between this version and the previous, so I decided to create new repo. The major differences are:
* MySQL instead of text files
* Admin features
* Remove workbook feature
* Workbooks list as inline keyboard

Other differences you can see in *assets/changelog.txt*

**Works on Heroku since 04.07.2021**
