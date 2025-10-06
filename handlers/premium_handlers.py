from aiogram.filters import Command, StateFilter
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.generated_keyboard import generated_keyboards
from lexicon import lexicon
from states import Premium

from validate_email import validate_email

router = Router()

@router.message(Command(commands="payment"))
async def process_payment(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon.payment_message)
    await state.set_state(Premium.payment)


async def process_payment_email(message: Message, state: FSMContext):
    email = message.text.strip()
    is_valid_with_domain_check = validate_email(email)
    if is_valid_with_domain_check:
        await message.answer(text=lexicon.email_message,
                             reply_markup=generated_keyboards(1, "Оплатить"))
        await state.update_data(email=email)
    else:
        await message.answer(text=lexicon.email_error)
        return


@router.callback_query(F.data == "Оплатить", StateFilter(Premium.payment))
async def process_payment_url(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Будет оплата")
    await state.clear()
    # код для обработки платежа


@router.callback_query(F.data == "Купить запросы")
async def process_buy_requests(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(text=lexicon.payment_message)
    await state.set_state(Payment.payment)
