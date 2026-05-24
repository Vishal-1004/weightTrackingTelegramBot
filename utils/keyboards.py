# utils/keyboards.py
from telebot import types

def main_menu():
    """Persistent keyboard stuck to the bottom of the screen."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_log = types.KeyboardButton("📝 Log Weight")
    btn_report = types.KeyboardButton("📊 View Progress Report")
    
    # Bottom row split perfectly into two equal halves
    btn_edit_delete = types.KeyboardButton("✏️ Delete/Edit Record")
    btn_help = types.KeyboardButton("ℹ️ Help")
    
    markup.add(btn_log, btn_report)
    markup.add(btn_edit_delete, btn_help)
    return markup

def goal_inline_menu():
    """Inline buttons embedded inside the chat bubble for onboarding selection."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_loss = types.InlineKeyboardButton("Weight Loss 📉", callback_data="goal_loss")
    btn_gain = types.InlineKeyboardButton("Weight Gain 📈", callback_data="goal_gain")
    
    markup.add(btn_loss, btn_gain)
    return markup

def edit_delete_choice_menu():
    """Inline menu to choose between editing or deleting a record."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_edit = types.InlineKeyboardButton("✏️ Edit Record", callback_data="action_edit")
    btn_delete = types.InlineKeyboardButton("🗑️ Delete Record", callback_data="action_delete")
    markup.add(btn_edit, btn_delete)
    return markup