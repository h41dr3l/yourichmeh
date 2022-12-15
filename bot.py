# gcloud functions deploy main --set-env-vars "TELEGRAM_TOKEN=5693741664:AAHL3tdQJVx6_ICfe7JZUEBM4dwbBND-o3Y" --runtime python38 --trigger-http --project=you-rich-meh
# curl "https://api.telegram.org/bot5693741664:AAHL3tdQJVx6_ICfe7JZUEBM4dwbBND-o3Y/setWebhook?url=https://us-central1-you-rich-meh.cloudfunctions.net/main"

import json
from datetime import datetime
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler,
)
import re
from currency_converter import CurrencyConverter

def write_json(dictionary):
    json_object = json.dumps(dictionary, indent=4)
    with open("data.json", "w") as outfile:
        outfile.write(json_object)
        
def read_json():
    with open('data.json', 'r') as openfile:
        json_object = json.load(openfile)
    return json_object

def get_date():
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year
    return day, month, year

def convert_currency(price, country):
    c = CurrencyConverter('https://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip')
    return round(float(c.convert(price, country.upper(), 'SGD')),2)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hi there! Enter 'MM/YYYY' to check how much you spent in a specific month. Enter 'Item, Price' to add a new spending")

def msg_handler(update: Update, context: CallbackContext):
    #get monthly
    pattern = "^\d{1,2}/\d{4}$"
    msg = update.message.text
    user = str(update.message.from_user.id)
    if re.search(pattern, msg) != None:
        dictionary = read_json()
        total = 0
        for day in dictionary[user][msg]:
            for item in dictionary[user][msg][f"{day}"]:
                total += float(dictionary[user][msg][f"{day}"][item])
        update.message.reply_text(f"You spent ${str(total)} in the month of {msg}")

        days = []
        amt = []
        message= ''
        for day in dictionary[user][msg]:
            total = 0
            days.append(int(day))
            for item in dictionary[user][msg][day]:
                total += float(dictionary[user][msg][day][item])
            amt.append(total)
            message += f'{str(day)}: ${str(total)}\n'
    
        message += f"\nYou spent an average of ${str(round(sum(amt)/len(amt),2))} per day"
        update.message.reply_text(message)

    #input amount
    pattern = "^[a-zA-Z]+, ([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))$"
    if re.search(pattern, msg) != None:
        dictionary = read_json()
        item_amt = msg.split(',')
        item = item_amt[0]
        price = item_amt[1]
        day, month, year = get_date()

        if str(user) not in dictionary:
            dictionary[user] = {}
        
        if f"{month}/{year}" not in dictionary[user]:
            dictionary[user][f"{month}/{year}"] = {}
            
        if f"{day}" not in dictionary[user][f"{month}/{year}"]:
            dictionary[user][f"{month}/{year}"][f"{day}"] = {}
            
        if item not in dictionary[user][f"{month}/{year}"][f"{day}"]:
            dictionary[user][f"{month}/{year}"][f"{day}"][item] = 0
            
        dictionary[user][f"{month}/{year}"][f"{day}"][item] = float(dictionary[user][f"{month}/{year}"][f"{day}"][item]) + float(price)
        write_json(dictionary)
        update.message.reply_text("Updated Successfully!")

    pattern = "^[a-zA-Z]+, ([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*)) ?[a-zA-Z]{3}$"
    if re.search(pattern, msg) != None:
        dictionary = read_json()
        item_amt = msg.split(',')
        item = item_amt[0]
        price = item_amt[1][0:-3]
        curr = item_amt[1][-3:]
        price = convert_currency(float(price), curr)
        day, month, year = get_date()

        if str(user) not in dictionary:
            dictionary[user] = {}
        
        if f"{month}/{year}" not in dictionary[user]:
            dictionary[user][f"{month}/{year}"] = {}
            
        if f"{day}" not in dictionary[user][f"{month}/{year}"]:
            dictionary[user][f"{month}/{year}"][f"{day}"] = {}
            
        if item not in dictionary[user][f"{month}/{year}"][f"{day}"]:
            dictionary[user][f"{month}/{year}"][f"{day}"][item] = 0
            
        dictionary[user][f"{month}/{year}"][f"{day}"][item] = float(dictionary[user][f"{month}/{year}"][f"{day}"][item]) + price
        write_json(dictionary)
        update.message.reply_text("Updated Successfully!")

    
def sum_today(update: Update, context: CallbackContext):
    dictionary = read_json()
    total = 0
    user = str(update.message.from_user.id)
    day, month, year = get_date()

    if str(day) not in dictionary[user][f"{month}/{year}"]:
        update.message.reply_text(f"You spent $0 today")
    else:
        for item in dictionary[user][f"{month}/{year}"][f"{day}"]:
            total += float(dictionary[user][f"{month}/{year}"][f"{day}"][item])
        update.message.reply_text(f"You spent ${str(total)} today")



def main():
    TOKEN = "5693741664:AAHL3tdQJVx6_ICfe7JZUEBM4dwbBND-o3Y"
    bot = Bot(TOKEN)
    updater = Updater(TOKEN, use_context=True)
        # Get dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today_spending", sum_today))
    dp.add_handler(MessageHandler(Filters.text, msg_handler))
    # dp.add_handler(MessageHandler(Filters.text, enter_amount))

    # dp.add_handler(InlineQueryHandler(inline_price))
    # dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
