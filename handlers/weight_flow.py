# handlers/weight_flow.py
from datetime import datetime
from utils import keyboards
from db.operations import (
    get_user, 
    get_weight_bounds, 
    get_all_weight_logs, 
    save_or_update_weight,
    has_logged_today,
    check_log_exists_on_date,
    delete_weight_log,
    update_weight_on_date
)

# Global helper normalization sets for fuzzy verification handling
YES_WORDS = ['yes', 'y', 'yeah', 'yup', 'yess', 'ok', 'sure', 'confirm']
NO_WORDS = ['no', 'n', 'nope', 'dont', 'cancel', 'stop']

def helper_format_log_table(logs):
    """Generates an aligned monospace history table layout text block."""
    table_header = "📅 Date       | ⚖️ Weight\n|------------|------------|\n"
    table_rows = ""
    for log_date, weight in logs:
        table_rows += f"| {log_date} | {weight:<6} kg |\n"
    return f"```text\n{table_header}{table_rows}```"

def validate_user_date(user_id, raw_text):
    """
    Validates user text input for dates.
    Returns (is_valid, formatted_date_string, error_message)
    """
    cleaned_text = raw_text.strip()
    try:
        # Enforce strict syntax parsing parameters
        parsed_date = datetime.strptime(cleaned_text, "%Y-%m-%d").date()
        date_str = parsed_date.isoformat()
    except ValueError:
        return False, None, "Format error! Please use the exactly specified `YYYY-MM-DD` syntax template format."

    # Verify if the date exists in the database
    if not check_log_exists_on_date(user_id, date_str):
        return False, None, "Data mismatch error! The date entry you provided could not be found in your tracking records."
        
    return True, date_str, "Valid"


def register_weight_handlers(bot):
    
    @bot.message_handler(func=lambda message: message.text == "📝 Log Weight")
    def ask_for_weight(message):
        msg = bot.send_message(message.chat.id, "Please send me your current weight in kg (e.g., 81.4):")
        bot.register_next_step_handler(msg, process_weight_log, bot)

    @bot.message_handler(func=lambda message: message.text == "📊 View Progress Report")
    def show_report(message):
        user_id = message.from_user.id
        user_profile = get_user(user_id)
        bounds = get_weight_bounds(user_id)
        
        if not user_profile or not bounds["current_weight"]:
            bot.send_message(message.chat.id, "⚠️ No weight data found yet! Please log your weight using the button below first.", reply_markup=keyboards.main_menu())
            return

        goal_type = user_profile[3]      
        target_weight = user_profile[4]  
        starting = bounds["starting_weight"]
        current = bounds["current_weight"]
        
        total_changed = current - starting
        distance_to_target = current - target_weight
        direction_emoji = "📉" if total_changed <= 0 else "📈"
        
        if goal_type.lower() == "loss":
            status_text = "🎉 *Goal Achieved!*" if distance_to_target <= 0 else f"🎯 You are *{abs(distance_to_target):.1f} kg* away from your target goal!"
        else: 
            status_text = "🎉 *Goal Achieved!*" if distance_to_target >= 0 else f"🎯 You are *{abs(distance_to_target):.1f} kg* away from your target goal!"

        report_msg = (
            "📊 *Your Live Progress Report*\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"🏁 *Starting Weight:* {starting:.1f} kg\n"
            f"💪 *Current Weight:* {current:.1f} kg ({direction_emoji} {total_changed:+.1f} kg)\n"
            f"🎯 *Target Weight:* {target_weight:.1f} kg\n\n"
            f"{status_text}\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "🔎 To view your entire historical tracking timeline, click here: /viewfullreport"
        )
        bot.send_message(message.chat.id, report_msg, parse_mode="Markdown", reply_markup=keyboards.main_menu())

    @bot.message_handler(commands=['viewfullreport'])
    def show_full_report(message):
        user_id = message.from_user.id
        logs = get_all_weight_logs(user_id)
        if not logs:
            bot.send_message(message.chat.id, "⚠️ You have not logged any weights yet.", reply_markup=keyboards.main_menu())
            return
        
        full_report_msg = "📋 *Complete Weight Log History*\n\n" + helper_format_log_table(logs)
        bot.send_message(message.chat.id, full_report_msg, parse_mode="Markdown", reply_markup=keyboards.main_menu())

    # 💡 NEW: UI Trigger route intercept for operations management
    @bot.message_handler(func=lambda message: message.text == "✏️ Delete/Edit Record")
    def handle_modification_menu(message):
        bot.send_message(
            message.chat.id, 
            "⚙️ *Record Management Options*\n\nWhat would you like to do with your logged history details?", 
            parse_mode="Markdown", 
            reply_markup=keyboards.edit_delete_choice_menu()
        )

    # Callback intercept route processor
    @bot.callback_query_handler(func=lambda call: call.data.startswith('action_'))
    def handle_modification_action(call):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        action = "edit" if call.data == "action_edit" else "delete"
        
        logs = get_all_weight_logs(user_id)
        if not logs:
            bot.send_message(call.message.chat.id, "⚠️ You don't have any weight logs recorded to alter.", reply_markup=keyboards.main_menu())
            return
            
        # Display the log matrix list table layout
        table_output = helper_format_log_table(logs)
        prompt_text = (
            f"📋 *Your Current Logs:*\n\n{table_output}\n"
            f"Please enter the specific *Date* of the record you wish to **{action.upper()}** "
            f"exactly as written above (Format: `YYYY-MM-DD`):"
        )
        
        msg = bot.send_message(call.message.chat.id, prompt_text, parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_capture_and_validate_date, bot, action)


# 💡 Sequential step workflow methods
def step_capture_and_validate_date(message, bot, action):
    user_id = message.from_user.id
    user_input = message.text
    
    is_valid, target_date, err_msg = validate_user_date(user_id, user_input)
    
    if not is_valid:
        # Query logs array list to display structural reference layout again
        logs = get_all_weight_logs(user_id)
        table_output = helper_format_log_table(logs)
        
        reprompt_msg = bot.send_message(
            message.chat.id,
            f"⚠️ *{err_msg}*\n\nPlease review your log table and type a valid matching entry date option below (Format: `YYYY-MM-DD`):\n\n{table_output}",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(reprompt_msg, step_capture_and_validate_date, bot, action)
        return

    # Direct traffic routing pathways based on structural intent actions
    if action == "delete":
        msg = bot.send_message(
            message.chat.id, 
            f"❗ *Confirmation Required*\nAre you absolutely sure you want to delete your log entry for *{target_date}*? (Yes / No)", 
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, step_confirm_delete, bot, target_date)
    elif action == "edit":
        msg = bot.send_message(
            message.chat.id, 
            f"📝 Enter the **new weight** value in kg to replace the entry on *{target_date}*:", 
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, step_capture_new_weight, bot, target_date)


def step_confirm_delete(message, bot, target_date):
    user_response = message.text.strip().lower()
    user_id = message.from_user.id
    
    if user_response in YES_WORDS:
        delete_weight_log(user_id, target_date)
        bot.send_message(message.chat.id, f"🗑️ The weight log entry for *{target_date}* has been deleted.", parse_mode="Markdown", reply_markup=keyboards.main_menu())
    elif user_response in NO_WORDS:
        bot.send_message(message.chat.id, "🚫 Operation cancelled. No records were deleted.", reply_markup=keyboards.main_menu())
    else:
        msg = bot.send_message(message.chat.id, "⚠️ Invalid response. Please confirm with a clear *Yes* or *No*:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_confirm_delete, bot, target_date)


def step_capture_new_weight(message, bot, target_date):
    user_input = message.text.strip()
    try:
        new_weight = float(user_input)
    except ValueError:
        msg = bot.send_message(message.chat.id, "⚠️ That didn't look like a valid number. Please enter a valid decimal number for weight:")
        bot.register_next_step_handler(msg, step_capture_new_weight, bot, target_date)
        return
        
    msg = bot.send_message(
        message.chat.id, 
        f"❗ *Confirmation Required*\nAre you sure you want to change the entry on *{target_date}* to *{new_weight} kg*? (Yes / No)", 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, step_confirm_edit, bot, target_date, new_weight)


def step_confirm_edit(message, bot, target_date, new_weight):
    user_response = message.text.strip().lower()
    user_id = message.from_user.id
    
    if user_response in YES_WORDS:
        update_weight_on_date(user_id, target_date, new_weight)
        bot.send_message(message.chat.id, f"🔄 The entry for *{target_date}* has been updated to *{new_weight} kg*.", parse_mode="Markdown", reply_markup=keyboards.main_menu())
    elif user_response in NO_WORDS:
        bot.send_message(message.chat.id, "🚫 Operation cancelled. No records were modified.", reply_markup=keyboards.main_menu())
    else:
        msg = bot.send_message(message.chat.id, "⚠️ Invalid response. Please confirm with a clear *Yes* or *No*:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_confirm_edit, bot, target_date, new_weight)


# Existing original logic workflow routines
def process_weight_log(message, bot):
    user_input = message.text
    user_id = message.from_user.id
    try:
        current_weight = float(user_input.strip())
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ That didn't look like a valid number. Tap '📝 Log Weight' to try again.", reply_markup=keyboards.main_menu())
        return

    if has_logged_today(user_id):
        msg = bot.send_message(message.chat.id, f"⚠️ You already logged a weight entry today.\nWould you like to update it to *{current_weight} kg*? (Yes / No)", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_update_confirmation, bot, current_weight)
    else:
        save_or_update_weight(user_id=user_id, weight=current_weight)
        bot.send_message(message.chat.id, f"✅ Successfully logged *{current_weight} kg* for today!", parse_mode="Markdown", reply_markup=keyboards.main_menu())

def process_update_confirmation(message, bot, pending_weight):
    user_response = message.text.strip().lower()
    user_id = message.from_user.id

    if user_response in YES_WORDS:
        save_or_update_weight(user_id=user_id, weight=pending_weight)
        bot.send_message(message.chat.id, f"🔄 Record updated successfully to *{pending_weight} kg*. Thank you!", parse_mode="Markdown", reply_markup=keyboards.main_menu())
    elif user_response in NO_WORDS:
        bot.send_message(message.chat.id, "🚫 No changes were made to today's entry. Thank you!", reply_markup=keyboards.main_menu())
    else:
        msg = bot.send_message(message.chat.id, "⚠️ I didn't quite get that. Please answer with a clear *Yes* or *No*:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_update_confirmation, bot, pending_weight)