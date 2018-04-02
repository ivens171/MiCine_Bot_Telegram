import time
import json
import requests
import urllib
from dbPendiente import DBPendiente
from dbVista import DBVista

dbP = DBPendiente()
dbV = DBVista()

TOKEN = '593198159:AAFGoUy8DQKqamzH25xHh4w-beZ2e0ovui4'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    respuesta = requests.get(url)
    contenido = respuesta.content.decode("utf8")
    return contenido


def get_json_from_url(url):
    contenido = get_url(url)
    js = json.loads(contenido)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        itemsP = dbP.get_items(chat)  ##
        itemsV = dbV.get_items(chat)  ##

        if text.startswith("/vistas"):
            send_message("Pelis Vistas\n", chat)
            itemsV = dbV.get_items(chat)  ##
            message = "\n".join(itemsV)
            send_message(message, chat)

        elif text == "/vista":
            keyboard = build_keyboard(itemsP)
            send_message("¿Qué película has visto?", chat, keyboard)

        # elif text == "/start":
        #     send_message(
        #         "Bienvenidos al bot de las pelis",
        #         chat)

        elif text.startswith("/pendientes"):
            send_message("Pelis Pendientes\n", chat)
            itemsP = dbP.get_items(chat)  ##
            message = "\n".join(itemsP)
            send_message(message, chat)

        elif text.startswith("/pendiente"):
            send_message("Pelis Pendientes\n", chat)
            textp=text[11:]
            dbP.add_item(textp, chat)  ##
            itemsP = dbP.get_items(chat)  ##
            message = "\n".join(itemsP)
            send_message(message, chat)

        elif text in itemsP:
            send_message("Pelis Vistas\n", chat)
            dbP.delete_item(text, chat)
            dbV.add_item(text, chat)  ##
            itemsV = dbV.get_items(chat)  ##
            message = "\n".join(itemsV)
            send_message(message, chat)
            ##

        elif text==("/novista"):
            keyboard = build_keyboard(itemsV)
            send_message("¿Qué película has visto?", chat, keyboard)

        elif text in itemsV:
            send_message("Pelis Vistas\n", chat)
            dbV.delete_item(text, chat)
            itemsV = dbV.get_items(chat)  ##
            message = "\n".join(itemsV)
            send_message(message, chat)



        else:
            continue
            # db.add_item(text, chat)  ##
            # items = db.get_items(chat)  ##
            # message = "\n".join(items)
            # send_message(message, chat)



def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

# def echo_all(updates):
#     for update in updates["result"]:
#         try:
#             text = update["message"]["text"]
#             chat = update["message"]["chat"]["id"]
#             send_message(text, chat)
#         except Exception as e:
#             print(e)


def main():
    dbP.setup()
    dbV.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            #echo_all(updates)
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
