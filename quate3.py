import json
import os
from filelock import FileLock
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
NOTES_FILE = 'notes.json'
LOCK_FILE = 'notes.lock'

class Assistant:
    def __init__(self, filename=NOTES_FILE, lockfile=LOCK_FILE):
        self.filename = filename
        self.lockfile = lockfile
        self.notes = []
        self.load_notes()

    def load_notes(self):
        if os.path.exists(self.filename):
            try:
                with FileLock(self.lockfile):
                    with open(self.filename, 'r', encoding='utf-8') as f:
                        self.notes = json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Файл пошкоджено або недоступний. Створюємо новий.")
                self.notes = []
                self.save_notes()
        else:
            self.notes = []

    def save_notes(self):
        with FileLock(self.lockfile):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def add_note(self, text, tags=None):
        if not text.strip():
            print("Помилка: нотатка не може бути порожньою")
            return False
        if tags is None:
            tags = []
        self.load_notes()
        note = {"text": text.strip(), "tags": [tag.strip() for tag in tags if tag.strip()]}
        self.notes.append(note)
        self.save_notes()
        print("Нотатку додано!")
        return True

    def list_notes(self):
        self.load_notes()
        if not self.notes:
            print("Нотаток немає")
            return
        print("\nСписок нотаток:")
        for i, note in enumerate(self.notes, 1):
            tags_str = ", ".join(note["tags"]) if note["tags"] else "без тегів"
            print(f"{i}. {note['text']} [{tags_str}]")

    def search_notes(self, keyword):
        self.load_notes()
        keyword = keyword.lower().strip()
        if not keyword:
            print("Помилка: введіть ключове слово для пошуку")
            return
        found = [note for note in self.notes if keyword in note["text"].lower() or any(keyword in tag.lower() for tag in note["tags"])]
        if not found:
            print(f"Нотаток з ключовим словом '{keyword}' не знайдено")
            return
        print(f"\nРезультати пошуку за '{keyword}':")
        for i, note in enumerate(found, 1):
            tags_str = ", ".join(note["tags"]) if note["tags"] else "без тегів"
            print(f"{i}. {note['text']} [{tags_str}]")


# --- Telegram Bot Setup ---

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
assistant = Assistant()

class NoteStates(StatesGroup):
    waiting_for_note_text = State()
    waiting_for_note_tags = State()
    waiting_for_search_keyword = State()

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply("Вітаю! Я бот для нотаток.\nСпробуй /help")

@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    await message.reply(
        "Команди:\n"
        "/add - додати нотатку\n"
        "/list - показати всі нотатки\n"
        "/search - пошук нотаток"
    )

@dp.message_handler(commands='add')
async def cmd_add(message: types.Message):
    await message.reply("Введи текст нотатки:")
    await NoteStates.waiting_for_note_text.set()

@dp.message_handler(state=NoteStates.waiting_for_note_text)
async def process_note_text(message: types.Message, state: FSMContext):
    await state.update_data(note_text=message.text)
    await message.reply("Введи теги через кому (або надішли порожній рядок, якщо без тегів):")
    await NoteStates.waiting_for_note_tags.set()

@dp.message_handler(state=NoteStates.waiting_for_note_tags)
async def process_note_tags(message: types.Message, state: FSMContext):
    data = await state.get_data()
    note_text = data.get("note_text")
    tags_text = message.text.strip()
    tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
    success = assistant.add_note(note_text, tags)
    if success:
        await message.reply("Нотатку додано!")
    else:
        await message.reply("Не вдалося додати нотатку.")
    await state.finish()

@dp.message_handler(commands='list')
async def cmd_list(message: types.Message):
    assistant.load_notes()
    if not assistant.notes:
        await message.reply("Список нотаток порожній.")
        return
    response = ""
    for i, note in enumerate(assistant.notes, 1):
        tags_str = ", ".join(note["tags"]) if note["tags"] else "без тегів"
        response += f"{i}. {note['text']} [{tags_str}]\n"
    await message.reply(response)

@dp.message_handler(commands='search')
async def cmd_search(message: types.Message):
    await message.reply("Введи ключове слово для пошуку:")
    await NoteStates.waiting_for_search_keyword.set()

@dp.message_handler(state=NoteStates.waiting_for_search_keyword)
async def process_search(message: types.Message, state: FSMContext):
    keyword = message.text.strip()
    assistant.load_notes()
    found = [note for note in assistant.notes if keyword.lower() in note["text"].lower() or any(keyword.lower() in tag.lower() for tag in note["tags"])]
    if not found:
        await message.reply("Нічого не знайдено за цим словом.")
    else:
        response = ""
        for i, note in enumerate(found, 1):
            tags_str = ", ".join(note["tags"]) if note["tags"] else "без тегів"
            response += f"{i}. {note['text']} [{tags_str}]\n"
        await message.reply(response)
    await state.finish()

# --- Console interface ---

def run_console():
    print("Консольний асистент нотаток")
    print("Команди:")
    print("/add - додати нотатку")
    print("/list - показати всі нотатки")
    print("/search - пошук нотаток")
    print("/exit - вийти")
    while True:
        command = input("\nВведіть команду: ").strip().lower()
        if command == '/exit':
            print("До побачення!")
            break
        elif command == '/add':
            text = input("Введіть текст нотатки: ")
            tags_input = input("Введіть теги через кому (або натисніть Enter, якщо без тегів): ")
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input.strip() else []
            assistant.add_note(text, tags)
        elif command == '/list':
            assistant.list_notes()
        elif command == '/search':
            keyword = input("Введіть ключове слово для пошуку: ")
            assistant.search_notes(keyword)
        else:
            print("Невідома команда.")

# --- Main ---

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'console':
        run_console()
    else:
        print("Запускаємо Telegram-бота...")
        executor.start_polling(dp, skip_updates=True)
