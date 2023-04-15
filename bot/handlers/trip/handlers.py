from aiogram import types
from aiogram.dispatcher import FSMContext
from bson import ObjectId

from bot.constants import TripConfigureType, ConfigureInterval
from bot.handlers import utils
from bot.handlers.base.constants import CHANGE_INTERVAL_MESSAGE
from bot.handlers.base.states import ChooseTripSearchState, TripConfigureState
from bot.handlers.keyboard import generate_trip_settings_inline_markup, generate_configure_interval_markup
from bot.handlers.utils import generate_trip_info, process_state_config_for_trip
from services.atlas.dto import LookingTripParams
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


async def choose_trip_to_start_searching(message: types.Message, **kwargs):
    text, markup = utils.generate_choose_trip_info(message.chat.id)
    await message.answer(text, reply_markup=markup)
    await ChooseTripSearchState.choose_trip.set()


async def handle_chosen_trip(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    if not ObjectId.is_valid(callback.data):
        return await callback.answer(callback.data)

    text, reply_markup = generate_trip_info(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )

    await state.update_data(chosen_trip_id=callback.data)
    await ChooseTripSearchState.configure_trip.set()


async def handle_configure_for_trip(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    if not isinstance(callback.data, str):
        return await callback.answer("Ошибка, попробуйте еще раз")

    match callback.data:

        case TripConfigureType.INTERVAL.value:
            await callback.message.edit_text(
                text=CHANGE_INTERVAL_MESSAGE,
                reply_markup=generate_configure_interval_markup()
            )

            await TripConfigureState.interval_config_trip.set()

        case TripConfigureType.STATE.value:
            state_data = await state.get_data()
            title, markup = await process_state_config_for_trip(callback.message, state_data['chosen_trip_id'])
            await callback.message.edit_text(title, reply_markup=markup)


async def handle_interval_config_for_trip(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    key = callback.data
    if not isinstance(key, str):
        return await callback.answer('Ошибка, попробуйте еще раз')

    state_data = await state.get_data()
    chosen_trip_id = state_data['chosen_trip_id']

    new_interval = ConfigureInterval.get(key)
    interval = int(new_interval.name.split("_")[1])

    mongo = Mongo(settings=MongoSettings())
    mongo.update_trip(chosen_trip_id, data={'interval': interval})
    trip_params: LookingTripParams = mongo.retrieve_trip_params(chosen_trip_id)

    callback.message.text = trip_params.title
    callback.message.reply_markup = generate_trip_settings_inline_markup(trip_params)


async def handle_configure_trip_back_button(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    if callback.data != 'configure_trip_back':
        return await callback.answer('Ошибка, попробуйте еще раз')

    text, markup = utils.generate_choose_trip_info(callback.message.chat.id)
    await callback.message.edit_text(text, reply_markup=markup)

    await state.finish()
    await ChooseTripSearchState.choose_trip.set()


async def handle_trip_interval_config_back_button(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    if callback.data != 'trip_interval_config':
        return await callback.answer('Ошибка, попробуйте еще раз')

    state_data = await state.get_data()
    chosen_trip_id = state_data['chosen_trip_id']

    text, reply_markup = generate_trip_info(chosen_trip_id)
    await callback.message.edit_text(text=text, reply_markup=reply_markup)

    await state.finish()
    await ChooseTripSearchState.configure_trip.set()
