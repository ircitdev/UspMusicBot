from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Dict


class Keyboards:

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="🎵 Создать песню"),
            KeyboardButton(text="📝 Есть стихи"),
        )
        builder.row(
            KeyboardButton(text="🎧 Мои песни"),
            KeyboardButton(text="💳 Баланс"),
        )
        builder.row(KeyboardButton(text="ℹ️ Помощь"))
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def remove() -> ReplyKeyboardRemove:
        return ReplyKeyboardRemove()

    @staticmethod
    def song_mode() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💡 Описать идею", callback_data="mode:idea")
        builder.button(text="📝 Готовый текст", callback_data="mode:lyrics")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def style_selection(styles: List[Dict], cache_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for style in styles:
            builder.button(
                text=f"{style['emoji']} {style['name']}",
                callback_data=f"style:{style['description']}:{cache_id}",
            )
        builder.button(text="✏️ Свой стиль", callback_data=f"style:custom:{cache_id}")
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def lyrics_style_selection() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        styles = [
            ("🎵 Pop", "pop"),
            ("🎸 Rock", "rock"),
            ("🎤 Hip-hop", "hip hop"),
            ("🎺 Jazz", "jazz"),
            ("🎹 Electronic", "electronic"),
            ("🎻 Classical", "classical"),
            ("🪕 Folk", "folk acoustic"),
            ("✏️ Свой стиль", "custom"),
        ]
        for label, data in styles:
            builder.button(text=label, callback_data=f"lstyle:{data}")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def voice_confirm(transcribed_text: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да, создать", callback_data="voice:confirm")
        builder.button(text="✏️ Исправить", callback_data="voice:edit")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def song_result(song_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💾 Сохранить в плейлист", callback_data=f"playlist:add:{song_id}")
        builder.button(text="🔄 Создать ещё", callback_data="song:new")
        builder.button(text="🎧 Мои песни", callback_data="songs:list")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def my_songs(page: int, total: int, per_page: int = 5) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        total_pages = (total + per_page - 1) // per_page
        if page > 1:
            builder.button(text="← Назад", callback_data=f"songs:page:{page - 1}")
        if page < total_pages:
            builder.button(text="Далее →", callback_data=f"songs:page:{page + 1}")
        builder.button(text="🎵 Создать новую", callback_data="song:new")
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def song_actions(song_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬇️ Скачать", callback_data=f"song:download:{song_id}")
        builder.button(text="💾 В плейлист", callback_data=f"playlist:add:{song_id}")
        builder.button(text="◀️ К списку", callback_data="songs:list")
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def balance_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="📦 Стартовый — 10 треков (299₽)", callback_data="buy:starter")
        builder.button(text="🔥 Популярный — 30 треков (799₽)", callback_data="buy:popular")
        builder.button(text="💎 Профессионал — 100 треков (1999₽)", callback_data="buy:pro")
        builder.button(text="📊 История транзакций", callback_data="balance:history")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def payment_method(package_id: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Оплатить картой (YooKassa)", callback_data=f"pay:yookassa:{package_id}")
        builder.button(text="💰 Криптовалюта (USDT/TON)", callback_data=f"pay:crypto:{package_id}")
        builder.button(text="◀️ Назад", callback_data="balance:main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def payment_link(url: str, package_id: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Перейти к оплате", url=url)
        builder.button(text="✅ Я оплатил", callback_data=f"pay:check:{package_id}")
        builder.button(text="❌ Отмена", callback_data="balance:main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Статистика", callback_data="admin:stats")
        builder.button(text="👥 Пользователи", callback_data="admin:users")
        builder.button(text="📢 Рассылка", callback_data="admin:broadcast")
        builder.button(text="🔧 Настройки", callback_data="admin:settings")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def cancel() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="❌ Отмена", callback_data="cancel")
        return builder.as_markup()
