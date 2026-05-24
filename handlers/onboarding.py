# handlers/onboarding.py
from telebot import types
from utils import text_templates, keyboards
from db.operations import get_user, create_user, update_user_goal

def register_onboarding_handlers(bot):
    
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.from_user.id
        existing_user = get_user(user_id)

        if existing_user:
            # Step 3: User exists -> Route directly to main app experience
            username = existing_user[1]
            bot.send_message(
                message.chat.id, 
                text_templates.WELCOME_BACK.format(name=username), 
                parse_mode="Markdown",
                reply_markup=keyboards.main_menu()
            )
        else:
            # Step 1: New User -> Commit profile initialization to database
            first_name = message.from_user.first_name
            create_user(user_id=user_id, name=first_name, phone=None)

            # Trigger Onboarding UI Questionnaire
            bot.send_message(
                message.chat.id, 
                text_templates.WELCOME_NEW, 
                parse_mode="Markdown", 
                reply_markup=keyboards.goal_inline_menu()
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('goal_'))
    def handle_goal_selection(call):
        goal = "Loss" if call.data == "goal_loss" else "Gain"
        bot.answer_callback_query(call.id)
        
        msg = bot.send_message(
            call.message.chat.id, 
            text_templates.ASK_TARGET_WEIGHT, 
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_target_weight_step, bot, goal)

def process_target_weight_step(message, bot, goal):
    user_input = message.text
    user_id = message.from_user.id
    
    try:
        target_weight = float(user_input)
    except ValueError:
        msg = bot.send_message(
            message.chat.id, 
            "⚠️ Please enter a valid numerical value (e.g., 72.5):"
        )
        bot.register_next_step_handler(msg, process_target_weight_step, bot, goal)
        return

    # Step 2 & 4: Update goal targets inside database
    update_user_goal(user_id=user_id, goal_type=goal, target_weight=target_weight)

    bot.send_message(
        message.chat.id, 
        text_templates.ONBOARDING_COMPLETE, 
        parse_mode="Markdown", 
        reply_markup=keyboards.main_menu()
    )