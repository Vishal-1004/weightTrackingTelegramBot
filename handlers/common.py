# handlers/common.py
from utils import text_templates, keyboards

def register_common_handlers(bot):
    
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda message: message.text == "ℹ️ Help")
    def handle_help(message):
        bot.send_message(
            message.chat.id, 
            text_templates.HELP_TEXT, 
            parse_mode="Markdown",
            reply_markup=keyboards.main_menu()
        )

    @bot.message_handler(commands=['contact'])
    def handle_contact(message):
        bot.send_message(
            message.chat.id, 
            text_templates.CONTACT_TEXT, 
            parse_mode="Markdown",
            # We don't want hyperlinks turning off link previews to ruin the chat bubble format
            disable_web_page_preview=False,
            reply_markup=keyboards.main_menu()
        )