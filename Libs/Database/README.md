# Heeto Database

Heeto uses Heroku's PostgreSQL extension to store useful information required by some core mechanics Heeto has. These are the tables used by Heeto:
> **NOTE:** Heeto bot is still a work in progress, so all tables can and will change overtime.
## Users
This table will be used by the **level**, **profile**, **ranking**, **economy** mechanics.
```sql
CREATE TABLE Users (ID bigint primary key not null, Name varchar(255), Servers bigint [], credits MONEY not null, level int not null, experience int not null, last_day_streak date not null, streak int not null, last_message_epoch int not null, description TEXT, cardColor TEXT, discriminator TEXT, avatar TEXT);
```

## Bot_Commands
This table will be used by the **Guilds** table to store if a command is enabled or disabled in a determined server.
```sql
    -- This is not fully implemented yet, but for test purposes use the following command:
    CREATE TABLE Bot_Commands (SPAM bool, Emojos bool);
```

## Guilds
This table will store server information.
```sql
    CREATE TABLE Guilds (ID bigint primary key not null, OwnerID bigint not null, EnabledCommands Bot_Commands);
```
