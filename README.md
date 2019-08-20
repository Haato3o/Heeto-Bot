# Heeto Bot
Heeto bot is my personal Discord bot, the original code isn't pretty so I decided to rewrite everything packing everything into classes. 

## Setting up Heeto bot on your own server
These are the required steps you need to follow to set up Heeto bot on your own server (hosting server, not the Discord one) if you want to host it on your own.
### Required
- PostgreSQL database
    - You can read more about databases Heeto currently uses by clicking [here](https://github.com/Haato3o/Heeto-Bot/tree/master/Libs/Database)
- Python 3.6 or later

## Commands

#### Tera
- **terastatus** *region*: Returns status of TERA servers (Default region is NA)

#### Spiral Knights
- **sk** *subcommand* *params*:
    - **Available subcommands:**
    - **gear** *gearName*: Returns info about *gearName*

#### Misc
- **echo** *message*: Makes the bot repeat the *message*.
- **emojos** *message*: Turns the *message* into an emoji copypasta
- **roll** *max*: Rolls the dice from 0 to *max* (Default = 20)"
- **heart** *background* *foreground*: Creates a heart using emotes
- **spam** *users*": Mentions *users* 3 times (up to 10 people)

### Bot documentation soon:tm: