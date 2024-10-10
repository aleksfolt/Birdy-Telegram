from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())