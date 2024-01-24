"""
Bot for financial records like sum on bank account, savings,
spendings of month with name and sums of things.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

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


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Send instructions when the command /start is issued
    await update.message.reply_text(rf'Use command /data to get records of bank acc and savings. '
                                    rf'Use command /thismonth to get records of this month '
                                    rf'or /prevmonth to get previous. '
                                    rf'Text what you spend money on in format "Bread 33.50" or "Income 3500". '
                                    rf'If it\'s your first usage then click /create')


async def create_tables(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # if there's no db or tables in that - create these

    if not os.path.isfile('fin_table.db') or os.path.getsize('fin_table.db') == 0:
        sql_for_bot.new_db()
        await update.message.reply_text('Done!')
    else:
        await update.message.reply_text('Already exist')


async def this_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # give user records of spendings in this month

    month_data = sql_for_bot.month_data('this')  # month_data is list
    if month_data:  # could be empty
        mon_str_data = str()
        for line in month_data:
            for elem in line:
                mon_str_data = f'{mon_str_data} {elem}'
            mon_str_data = f'{mon_str_data}\n'
        await update.message.reply_text(mon_str_data)
    else:
        await update.message.reply_text('No records in this month.')


async def prev_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # give user records of spendings in previous month

    month_data = sql_for_bot.month_data('prev')  # month_data is list
    if month_data:  # could be empty
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
    message = update.message.text
    some_tuple = tuple(message.split())

    if len(some_tuple) == 2:
        try:
            sql_for_bot.ins_prod_data(some_tuple[0], float(some_tuple[1]))
        except ValueError:
            await update.message.reply_text('Please, use format "Something 200.50"')
        else:
            last_record = sql_for_bot.take_bal_data()
            sql_for_bot.check_date()
            calcul = sql_for_bot.calc_bal(some_tuple[0], float(some_tuple[1]), last_record)
            sql_for_bot.ins_bal_data(calcul[0], calcul[1])
            await update.message.reply_text('Acknowledged!')
    else:
        await update.message.reply_text('Please, use format "Something 2000.50"')


async def giver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    balance = sql_for_bot.take_bal_data()
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
    application.add_handler(CommandHandler('thismonth', this_month))
    application.add_handler(CommandHandler('prevmonth', prev_month))

    # on non command i.e. message take product and sum of it
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, taker))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
