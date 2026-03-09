from aiogram.fsm.state import State, StatesGroup


class SongCreationStates(StatesGroup):
    # Выбор режима
    waiting_for_mode = State()

    # Режим: идея → песня
    waiting_for_idea = State()
    waiting_for_style_choice = State()
    waiting_for_custom_style = State()
    generating_lyrics = State()
    lyrics_review = State()
    generating_song = State()

    # Режим: готовые стихи
    waiting_for_lyrics = State()
    waiting_for_lyrics_style = State()


class BalanceStates(StatesGroup):
    waiting_for_package = State()
    waiting_for_payment_method = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_user_search = State()
    waiting_for_balance_change = State()
    waiting_for_balance_amount = State()
