# Heeto core mechanics
## Level
Heeto bot has a level mechanic, basically whenever an user talks, they get a random amount of experience.
> **Note:** This system has a cooldown of 60 seconds, so spamming messages will not reward you with experience.

### How required experience for next level is calculated?
The total experience required to level up is calculated by the following formula:
```py
    ExpRequired = (100 + (100 * level) * (level / 100))
```

### Level commands
- **level** *subcommand or user*
    - **user**
    - **Available subcommands**
        - TODO