import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# 🔧 Настройки
TOKEN = "7513338167:AAGtuPE90F5XnSfvdRkeME0lLbFBn7nET9M"  # 🔹 Твой токен бота (замени!)
ADMINS = {1302073426}  # 🔹 Список ID админов
PASSWORD = "bebeshka"  # 🔹 Пароль для входа
authorized_admins = set()  # 🔹 Авторизованные админы

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📄 Логи
LOG_FILE = "bot_logs.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# 📌 Машина состояний (FSM) для обработки пароля
class AuthState(StatesGroup):
    waiting_for_password = State()

async def send_log(message: str):
    """Отправляет логи в Telegram администраторам."""
    logging.info(message)
    for admin in authorized_admins:
        try:
            await bot.send_message(admin, f"📝 Лог: {message}")
        except Exception as e:
            logging.error(f"Ошибка отправки лога: {e}")

@dp.message(Command("login"))
async def login(message: types.Message, state: FSMContext):
    """Авторизация администратора."""
    if message.from_user.id in authorized_admins:
        await message.answer("✅ Вы уже авторизованы.")
    else:
        await message.answer("🔑 Введите пароль:")
        await state.set_state(AuthState.waiting_for_password)

@dp.message(AuthState.waiting_for_password)
async def check_password(message: types.Message, state: FSMContext):
    """Проверяет пароль и добавляет админа в список."""
    if message.text == PASSWORD and message.from_user.id in ADMINS:
        authorized_admins.add(message.from_user.id)
        await message.answer("✅ Авторизация успешна! Теперь вы можете смотреть логи.")
    else:
        await message.answer("❌ Неверный пароль.")
    await state.clear()  # Очистка состояния

@dp.message(Command("logout"))
async def logout(message: types.Message):
    """Выход администратора."""
    if message.from_user.id in authorized_admins:
        authorized_admins.remove(message.from_user.id)
        await message.answer("🚪 Вы вышли из системы.")
    else:
        await message.answer("❌ Вы не авторизованы.")

@dp.message(Command("logs"))
async def send_logs(message: types.Message):
    """Отправляет файл логов авторизованным админам."""
    if message.from_user.id in authorized_admins:
        try:
            file = FSInputFile(LOG_FILE)
            await message.answer_document(file)
        except Exception as e:
            await message.answer(f"Ошибка при отправке логов: {e}")
    else:
        await message.answer("❌ Вам нужно авторизоваться. Используйте /login.")

@dp.message(Command("clear_logs"))
async def clear_logs(message: types.Message):
    """Очищает логи."""
    if message.from_user.id in authorized_admins:
        try:
            with open(LOG_FILE, "w") as file:
                file.write("")
            await message.answer("🗑 Логи успешно очищены.")
        except Exception as e:
            await message.answer(f"Ошибка при очистке логов: {e}")
    else:
        await message.answer("❌ Вам нужно авторизоваться. Используйте /login.")

@dp.message(Command("status"))
async def check_status(message: types.Message):
    """Проверяет, авторизован ли пользователь."""
    if message.from_user.id in authorized_admins:
        await message.answer("✅ Вы авторизованы.")
    else:
        await message.answer("❌ Вы не авторизованы. Используйте /login.")

@dp.message()
async def handle_message(message: types.Message):
    """Логирует все текстовые сообщения, кроме команд."""
    if message.text.startswith("/"):
        return  # Игнорируем команды
    log_message = f"📩 {message.from_user.id} ({message.from_user.username}): {message.text}"
    logger.info(log_message)
    await send_log(log_message)

async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
