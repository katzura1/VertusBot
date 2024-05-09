[<img src="https://img.shields.io/badge/Telegram-%40Me-orange">](https://t.me/redberry7)


## Screenshot
![App Screenshot](https://raw.githubusercontent.com/katzura1/VirtusBot/main/demo.png)



## Functionality
| Functional                                                     | Supported |
|----------------------------------------------------------------|:---------:|
| Multithreading                                                 |     ✅     |
| Binding a proxy to a session                                   |     ✅     |
| Auto Upgrade Farm, Storage and Population                      |     ✅     |
| Support tdata / pyrogram .session / telethon .session          |     ✅     |

## [Settings](https://github.com/katzura1/VirtusBot/blob/main/.env.example)
| Настройка                | Описание                                                                                 |
|--------------------------|------------------------------------------------------------------------------------------|
| **API_ID / API_HASH**    | Platform data from which to launch a Telegram session _(stock - Android)_                |
| **USE_PROXY_FROM_FILE**  | Whether to use proxy from the `bot/config/proxies.txt` file (True / False)               |

## Installation
You can download [**Repository**](https://github.com/katzura1/VirtusBot) by cloning it to your system and installing the necessary dependencies:
```shell
~ >>> git clone https://github.com/katzura1/VertusBot.git
~ >>> cd VertusBot

# If you are using Telethon sessions, then clone the "converter" branch
~ >>> git clone https://github.com/katzura1/VertusBot.git -b converter
~ >>> cd VertusBot

#Linux
~/VertusBot >>> python3 -m venv venv
~/VertusBot >>> source venv/bin/activate
~/VertusBot >>> pip3 install -r requirements.txt
~/VertusBot >>> cp .env-example .env
~/VertusBot >>> nano .env # Here you must specify your API_ID and API_HASH , the rest is taken by default
~/VertusBot >>> python3 main.py

#Windows
~/VertusBot >>> python -m venv venv
~/VertusBot >>> venv\Scripts\activate
~/VertusBot >>> pip install -r requirements.txt
~/VertusBot >>> copy .env-example .env
~/VertusBot >>> # Specify your API_ID and API_HASH, the rest is taken by default
~/VertusBot >>> python main.py
```

Also for quick launch you can use arguments, for example:
```shell
~/VertusBot >>> python3 main.py --action (1/2)
# Or
~/VertusBot >>> python3 main.py -a (1/2)

#1 - Create session
#2 - Run clicker
```

## Reference Code Structure and ReadMe

- [Shamhi](https://github.com/shamhi)
