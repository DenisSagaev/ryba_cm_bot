from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from getters import check_limits
from handlers.generating_handlers import correct_row_handler, error_row_handler, no_text, correct_coll_handler
from lexicon import generating_messages
from states import ContentPlan
from utils.functions import split_str


gen_dialog = Dialog(
    Window(
        Const(text=generating_messages.start_generating),

        TextInput(id="rows",
                  type_factory=split_str,
                  on_success=correct_row_handler,
                  on_error=error_row_handler,
                  ),

        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        state=ContentPlan.rows,
        getter=check_limits),

    Window(
        Const(text=generating_messages.column_message),
        TextInput(id="column",
                  type_factory=split_str,
                  on_success=correct_coll_handler,
                  on_error=error_row_handler),

        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),

        state=ContentPlan.columns,
    ),

    Window(
        Const(generating_messages.done_message),
        Button(Const("Вперед"), id="go", on_click=generate_response),
        Button(Const("Начать сначала"), id="new_gen", on_click=process_cp_command),
           state=ContentPlan.done
           ),

    Window(
        Const(text=generating_messages.result_message),
        Button(Const("Еще темы"), id="themes", on_click=generate_response),
        Button(Const("Начать сначала"), id="new_gen", on_click=process_cp_command),
        state=ContentPlan.result
    )
)