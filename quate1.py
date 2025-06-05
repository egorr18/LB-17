import json
import os

class Assistant:
    def __init__(self, filename='notes.json'):
        self.filename = filename
        self.notes = []
        self.load_notes()
    
    def load_notes(self):
        """Завантажує нотатки з JSON-файлу"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
    
    def save_notes(self):
        """Зберігає нотатки у JSON-файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def add_note(self, note: str):
        """Додає нову нотатку"""
        if note.strip():  # Перевіряємо, що нотатка не порожня
            self.notes.append(note.strip())
            self.save_notes()
            print("Нотатку додано!")
        else:
            print("Помилка: нотатка не може бути порожньою")
    
    def list_notes(self):
        """Виводить список усіх нотаток"""
        if not self.notes:
            print("Нотаток немає")
            return
        
        print("\nСписок нотаток:")
        for i, note in enumerate(self.notes, 1):
            print(f"{i}. {note}")
    
    def search_notes(self, keyword: str):
        """Шукає нотатки за ключовим словом"""
        if not keyword.strip():
            print("Помилка: введіть ключове слово для пошуку")
            return
        
        found_notes = [
            note for note in self.notes 
            if keyword.lower() in note.lower()
        ]
        
        if not found_notes:
            print(f"Нотаток з ключовим словом '{keyword}' не знайдено")
            return
        
        print(f"\nРезультати пошуку за '{keyword}':")
        for i, note in enumerate(found_notes, 1):
            print(f"{i}. {note}")


def main():
    assistant = Assistant()
    print("Консольний асистент для нотаток. Доступні команди:")
    print("/add - додати нотатку")
    print("/list - переглянути всі нотатки")
    print("/search - пошук нотаток")
    print("/exit - вийти")
    
    while True:
        command = input("\nВведіть команду: ").strip().lower()
        
        if command == '/exit':
            print("До побачення!")
            break
        
        elif command == '/add':
            note = input("Введіть текст нотатки: ")
            assistant.add_note(note)
        
        elif command == '/list':
            assistant.list_notes()
        
        elif command == '/search':
            keyword = input("Введіть ключове слово для пошуку: ")
            assistant.search_notes(keyword)
        
        else:
            print("Невідома команда. Спробуйте ще раз.")


if __name__ == "__main__":
    main()