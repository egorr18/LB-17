import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = 'YOUR_BOT_TOKEN_HERE' 
NOTES_FILE = "notes.json"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class NoteStates(StatesGroup):
    waiting_for_note_text = State()
    waiting_for_search_keyword = State()

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)

def add_note(text):
    notes = load_notes()
    notes.append(text)
    save_notes(notes)

def search_notes(keyword):
    notes = load_notes()
    return [note for note in notes if keyword.lower() in note.lower()]

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply("Вітаю! Я бот для роботи з нотатками.\nСпробуй /help")

@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    await message.reply(
        "Доступні команди:\n"
        "/add – додати нотатку\n"
        "/list – переглянути всі нотатки\n"
        "/search – знайти нотатки за ключовим словом"
    )

@dp.message_handler(commands='add')
async def cmd_add(message: types.Message):
    await message.reply("Введи текст нотатки:")
    await NoteStates.waiting_for_note_text.set()

@dp.message_handler(state=NoteStates.waiting_for_note_text)
async def process_note_text(message: types.Message, state: FSMContext):
    add_note(message.text)
    await message.reply("Нотатку збережено!")
    await state.finish()

@dp.message_handler(commands='list')
async def cmd_list(message: types.Message):
    notes = load_notes()
    if notes:
        response = "\n\n".join([f"{i+1}. {note}" for i, note in enumerate(notes)])
    else:
        response = "Список нотаток порожній."
    await message.reply(response)

@dp.message_handler(commands='search')
async def cmd_search(message: types.Message):
    await message.reply("Введи ключове слово для пошуку:")
    await NoteStates.waiting_for_search_keyword.set()

@dp.message_handler(state=NoteStates.waiting_for_search_keyword)
async def process_search(message: types.Message, state: FSMContext):
    results = search_notes(message.text)
    if results:
        response = "\n\n".join(results)
    else:
        response = "Нічого не знайдено за цим словом."
    await message.reply(response)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
