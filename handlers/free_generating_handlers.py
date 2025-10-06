from aiogram import Router, F
from aiogram.enums import ChatAction, ContentType, ParseMode
from aiogram.loggers import event
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput

from getters import check_limits
from keyboards.generated_keyboard import generated_keyboards
from lexicon import generating_messages, premium_messages
from utils.functions import split_str, split_message
from open_ai.open_ai import get_answer_chat_gpt
from database.functions import update_counter
from database.models import users_table
from states import ContentPlan, Premium, PremiumContentPlan
from config_data.config import admin_ids

from aiogram_dialog import Dialog, DialogManager, Window, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button, Column, Row, Group
from aiogram_dialog.widgets.text import Const, Format, Case

# Создаем экземпляр роутера
router = Router()



async def check_limits_for_button(callback: CallbackQuery, button: Button, manager: DialogManager, **kwargs):
    user_id = manager.event.from_user.id
    await check_limits(int(user_id), manager)


async def correct_coll_handler(message: Message,
                               widget: ManagedTextInput,
                               dialog_manager: DialogManager,
                               text: str) -> None:
    dialog_manager.dialog_data.update(целевая_аудитория=text)
    await dialog_manager.next(show_mode=ShowMode.AUTO)


async def correct_row_handler(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              text: str) -> None:
    dialog_manager.dialog_data.update(продукты=text)
    await dialog_manager.next(show_mode=ShowMode.AUTO)


async def error_row_handler(message: Message,
                            widget: ManagedTextInput,
                            dialog_manager: DialogManager,
                            error: Exception) -> None:
    await message.answer(generating_messages.row_col_error)


async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer(text='Вы ввели вообще не текст!')


async def generate_response(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    event_dialog = None
    if isinstance(dialog_manager.event, CallbackQuery):
        event_dialog = dialog_manager.event.message
    elif isinstance(dialog_manager.event, Message):
        event_dialog = dialog_manager.event

    if event_dialog is None:
        raise TypeError("Неопределенный тип сообщения")

    data = dialog_manager.dialog_data

    try:
        await event_dialog.bot.send_chat_action(chat_id=event_dialog.chat.id,
                                                       action=ChatAction.TYPING)
        content = await get_answer_chat_gpt(data)
        check_content = await split_message(content)
        await update_counter(users_table, int(event_dialog.from_user.id))

        for i, el in enumerate(check_content):
            if i == len(check_content) - 1:
                await event_dialog.answer(text=el)
            else:
                await event_dialog.answer(text=el)
        await dialog_manager.switch_to(ContentPlan.result, ShowMode.AUTO)

    except Exception as e:
        await event_dialog.answer(text=f"{e}",
                                         reply_markup=generated_keyboards(1, "Начать сначала"))
        await dialog_manager.reset_stack()


@router.message(Command(commands="gen"))
async def process_generating_command(_, dialog_manager: DialogManager):
    await dialog_manager.done()
    await check_limits(_, _, dialog_manager)




@router.callback_query(F.data.regexp(r"^Еще темы"))
async def process_more_themes(callback: CallbackQuery, dialog_manager: DialogManager):
    limit = await check_limits(dialog_manager)
    if not limit:
        await dialog_manager.done(show_mode=ShowMode.AUTO)
        await callback.message.answer(text=generating_messages.not_limit,
                                      reply_markup=generated_keyboards(1,
                                                                       "Оформить премиум"))
