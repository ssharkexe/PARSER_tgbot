# Парсер сайтов для сравнения цен на аддоны для мобильных игр. Демонстрация работы с ORM (peewee), requests, re, beautifulsoup, graphql

## Основная информация

Функциональность была реализована по запросу: необходимо было сравнивать цены на аддоны для мобильных игр на маркетплейсах seagm.com и codashop.com, UI в telegram для удобства. Парсер создан для постоянной работы, поэтому он в корутине с рандомной периодичностью (чтобы избежать блокировки) собирает со страниц с указанными играми информацию и складывает в базу (sqlite).

Бот в комплекте на библиотеке aiogram в режиме поллинга, сам парсер на синхронной requests, ORM на синхронной peewee, хранение sqlite.

Оценить работу можно тут @coda_parser_bot.
<br/><br/>
## Зависимости и требования

Python 3.9+, зависимости из requirements
<br/><br/>
**Из чего состоит бот**

1. Хранение: sqlite база в файле, обращение к ней через ORM (peewee), классы с таблицами (+индексы) описаны в dbdata.py, там же общие функции работы с данными. Основная таблица с данными о стоимости аддонов - gamesaddon
2. НСИ: было решено хранить относительные url на страницы с нужными играми в отдельной таблице. Справочники регионов и форматов оплаты также в отдельных таблицах. 
3. Парсер codashop.com работает через http POST запрос к api graphql codashop.com. В заголовке запроса указываем access token (полученный при открытии страницы в браузере), url страницы с требуемой игрой, далее в теле уходит сам query запрос с необходимыми полями. Результат складываем в json, далее в цикле из списка вытягиваем нужные поля и складываем в базу.
4. Парсер seagm.com работает через http get и c помощью beautifulsoup вытягивает из полученного html блок с определенным заголовком, далее через регулярные выражения пробегается по полученному куску и складывает нужные данные в список, из которого уже пишем в базу через ORM.  
    4.1 Есть особенность, простым http get данные в HTML не приходят, срабатывает защита csrf токена + не сохраняется настройка валюты и региона. Поэтому сначала через get получаем csrf токен, устанавливаем в куки идентификатор seagm_store_id и затем в http POST указываем необходимые регион, валюту и url игры:
    ```
    def get_seagm_data()
    ```
    После этого спокойно считываем данные с html

5. Сам бот формирует список игр (inline клавиатура), которые есть в обоих магазинах, отображает последнюю дату обновления данных и отображает цены аддонов (при совпадении названий аддонов объединяет их в один блок текста), а также:

    5.1 Есть возможность вручную обновить данные с магазинов
    
    5.2 Есть возможность вручную сменить регион
    
    5.3 Есть возможность получить csv файл с полными данными таблицы gamesaddon
<br/><br/>
## Установка и запуск.

Запустить можно разными способами (локально на linux или на vps c linux):

Через docker (считаем, что docker у вас уже установлен, dockerfile в комплекте, нужно лишь передать при запуске переменную с токеном вашего бота):
```
$ git clone https://github.com/ssharkexe/PARSER_tgbot.git
$ cd PARSER_tgbot
$ docker run --rm -it -e TELEGRAM_TOKEN=ВАШ_ТОКЕН $(docker build -q .)
```

Просто сложить в папку и запустить (считаем, что pyhton в системе установлен, создаем виртуальное окружение и туда ставим зависимости, также не забыть о токене)
```
$ git clone https://github.com/ssharkexe/PARSER_tgbot.git
$ cd PARSER_tgbot
$ python3 -m venv venv
$ source venv/bin/activate 
$ pip install -r requirements.txt 
$ export TELEGRAM_TOKEN=ВАШ_ТОКЕН
$ python3 main.py
```

Сложить в папку и запустить как сервис (считаем, что pyhton в системе установлен):
```
$ git clone https://github.com/ssharkexe/PARSER_tgbot.git
$ cd PARSER_tgbot
$ pip install -r requirements.txt
$ export TELEGRAM_TOKEN=ВАШ_ТОКЕН
```

Открываем папку /etc/systemd/system
Создаем файл:
```
$ sudo nano BOT.service
```
Заполняем файл:
```
[Unit]
Description=Telegram bot
Wants=network.target
After=network.target

[Service]
WorkingDirectory=ПУТЬ ДО ПАПКИ С РЕПОЗИТОРИЕМ
ExecStart=/usr/bin/python3 main.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```
И запустить весь проект:
```
$ systemctl enable BOT.service
$ systemctl start BOT.service
```

<br/><br/>
## Заметки
Если вылезут баги, прошу оформить Issue.