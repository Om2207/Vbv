import logging
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import telegram.ext.filters as filters
import requests
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

API_URL = "https://api.adwadev.com/api/vbvapi.php?bin={}"

# Extract BIN from CC
def extract_bin(cc):
    return cc[:6]

# Check VBV status using the API
def check_vbv(bin):
    url = API_URL.format(bin)
    response = requests.get(url)
    return response.json()

# Format the response for better readability
def pretty_print_response(cc, response):
    formatted_response = f"""
    CC: {cc}
    BIN: {response['bin']}
    Status: {response['status']}
    Response: {response['response']}
    """
    return formatted_response

# Process multiple CCs
def process_ccs(cc_list):
    results = []
    for cc in cc_list:
        bin = extract_bin(cc)
        response = check_vbv(bin)
        formatted_response = pretty_print_response(cc, response)
        results.append(formatted_response)
    return results

# Read CCs from a file
def read_ccs_from_file(file_path):
    with open(file_path, 'r') as file:
        ccs = file.read().splitlines()
    return ccs

# Write results to a file
def write_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        for result in results:
            file.write(result + '\n')

# Start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me CC numbers or upload a txt file containing CCs to check VBV status.')

# Handle text messages containing CCs
def handle_message(update: Update, context: CallbackContext) -> None:
    cc_list = update.message.text.split('\n')
    results = process_ccs(cc_list)
    response_text = "\n\n".join(results)
    update.message.reply_text(response_text)

# Handle txt file upload
def handle_document(update: Update, context: CallbackContext) -> None:
    file = context.bot.get_file(update.message.document.file_id)
    file_path = 'input_ccs.txt'
    file.download(file_path)
    
    cc_list = read_ccs_from_file(file_path)
    results = process_ccs(cc_list)
    
    output_file_path = 'output_results.txt'
    write_results_to_file(results, output_file_path)
    
    with open(output_file_path, 'rb') as output_file:
        update.message.reply_document(document=InputFile(output_file), filename=output_file_path)

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's token
    updater = Updater("6972425077:AAG1-KTOtuR-qVO6siEP1sOnyilWbds8Sy4", use_context=True)
    
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.Text() & ~filters.COMMAND, handle_message))
    dispatcher.add_handler(MessageHandler(filters.Document.MIME_TYPE("text/plain"), handle_document))
    
    dispatcher.add_error_handler(error)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
