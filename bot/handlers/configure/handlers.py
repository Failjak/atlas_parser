from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from bot.constants import DEFAULT_INTERVAL, ConfigureInterval, ConfigureButtons
from bot.handlers.configure.states import ConfigureState
from bot.handlers.keyboard import generate_configure_inline_markup, configure_button_to_markups


async def configurations(message: types.Message, **kwargs):
    markup = generate_configure_inline_markup()
    await message.answer("Конфигурация:", reply_markup=markup)
    await ConfigureState.choose_configure.set()


async def _process_configurations(callback_query: types.CallbackQuery, state: FSMContext):
    cq_data = callback_query.data

    user_id = callback_query.from_user.id
    dispatcher = Dispatcher.get_current()

    msg = "Текущий интервал - {} мин\nДля изменения интервала, выберите один из вариантов " \
          "(после изменения перезапустите поиск):"

    if ConfigureButtons.get(cq_data) == ConfigureButtons.INTERVAL:
        data = await dispatcher.storage.get_data(user=user_id)

        markup_generator = configure_button_to_markups.get(callback_query.data)

        await callback_query.message.answer(msg.format(data.get('interval', DEFAULT_INTERVAL)),
                                            reply_markup=markup_generator(**data))

    elif new_interval := ConfigureInterval.get(cq_data):
        interval = new_interval.name.split("_")[1]
        await dispatcher.storage.update_data(user=user_id, data={"interval": interval})

        markup = callback_query.message.reply_markup
        try:
            await callback_query.message.edit_text(msg.format(interval), reply_markup=markup)
        except MessageNotModified:
            pass
