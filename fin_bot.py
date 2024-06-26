"""
Bot for financial records like sum on bank account, savings,
spendings of month with name and sums of things.

Usage:
Text what you spend money on or use commands to see record of spendings, bank acc and savings

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import sql_for_bot
import os.path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import bot_token

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MESSAGE_MAX_LENGTH = 4096


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Send instructions when the command /start is issued
    user = update.message.from_user.username.lower()
    await update.message.reply_text(f'Hi there {user}!\n'
                                    + 'Use command /data to get records of bank acc and savings.\n'
                                    + 'Use command /this_month to get records of this month\n'
                                    + 'or /prev_month to get previous.\n'
                                    + '/too_many to get records about most expensive prod in prev month.\n'
                                    + 'Text what you spend money on in format "Bread 33.50" or "Income 3500".\n')


async def create_tables(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # if there's no db or tables in that - create these

    if not os.path.isfile('fin_table.db') or os.path.getsize('fin_table.db') == 0:
        sql_for_bot.new_db()
        await update.message.reply_text('Done!')
    else:
        await update.message.reply_text('Already exist')


async def this_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # give user records of spending in this month

    user = update.message.from_user.username.lower()
    month_data = sql_for_bot.month_data('this', user)  # month_data is list
    if month_data:  # can be empty
        month_str_data = str()
        for line in month_data:
            for elem in line:
                month_str_data = f'{month_str_data} {elem}'
            month_str_data = f'{month_str_data}\n'
        if len(month_str_data) >= MESSAGE_MAX_LENGTH:
            mid_lane = len(month_str_data) // 2
            await update.message.reply_text(month_str_data[:mid_lane])
            await update.message.reply_text(month_str_data[mid_lane:])
        await update.message.reply_text(month_str_data)
    else:
        await update.message.reply_text('No records in this month.')


async def prev_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # give user records of spendings in previous month

    user = update.message.from_user.username.lower()
    month_data = sql_for_bot.month_data('prev', user)  # month_data is list
    if month_data:  # can be empty
        month_str_data = str()
        for line in month_data:
            for elem in line:
                month_str_data = f'{month_str_data} {elem}'
            month_str_data = f'{month_str_data}\n'
        if len(month_str_data) >= MESSAGE_MAX_LENGTH:
            mid_lane = len(month_str_data) // 2
            await update.message.reply_text(month_str_data[:mid_lane])
            await update.message.reply_text(month_str_data[mid_lane:])
        await update.message.reply_text(month_str_data)
    else:
        await update.message.reply_text('No records in previous month.')


async def most_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # give records about most valuable products in previous month

    user = update.message.from_user.username.lower()
    month_data = sql_for_bot.most_val_prev_month(user)
    if month_data:
        month_str_data = str()
        for line in month_data:
            for elem in line:
                month_str_data = f'{month_str_data} {elem}'
            month_str_data = f'{month_str_data}\n'
        await update.message.reply_text(month_str_data)
    else:
        await update.message.reply_text('No records in previous month.')


async def taker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Take data to change database
    user = update.message.from_user.username.lower()
    message = update.message.text
    some_tuple = tuple(message.split())

    if len(some_tuple) == 2:
        try:
            sql_for_bot.ins_prod_data(user, some_tuple[0], float(some_tuple[1]))
        except ValueError:
            await update.message.reply_text('Please, use format "Something 200.50"')
        else:
            last_record = sql_for_bot.take_bal_data(user)
            sql_for_bot.check_date(user)
            calcul = sql_for_bot.calc_bal(some_tuple[0], float(some_tuple[1]), last_record)
            sql_for_bot.ins_bal_data(user, calcul[0], calcul[1])
            await update.message.reply_text('Acknowledged!')
    else:
        await update.message.reply_text('Please, use format "Something 2000.50"')


async def giver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user.username.lower()
    balance = sql_for_bot.take_bal_data(user)
    if balance:
        await update.message.reply_text(f'{balance[0]} | sum: {round(balance[1], 2)} | savings: {round(balance[2], 2)}')
    else:
        await update.message.reply_text('No records')


def main() -> None:
    # Start the bot.
    # Create the Application and pass it bot's token.
    application = Application.builder().token(bot_token.token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('create', create_tables))
    application.add_handler(CommandHandler('data', giver))
    application.add_handler(CommandHandler('this_month', this_month))
    application.add_handler(CommandHandler('prev_month', prev_month))
    application.add_handler(CommandHandler('too_many', most_val))

    # on non command i.e. message take product and sum of it
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, taker))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
