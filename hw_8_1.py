import re, pickle
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if phone not in self.phones:
            self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            idx = self.phones.index(old_phone)
            self.phones[idx] = Phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "Not specified"
        return f"Contact name: {self.name}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now().date()
        for record in self.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                if birthday_date - today <= timedelta(days=7):
                    upcoming_birthdays.append((record.name.value, birthday_date.strftime("%d.%m.%Y")))
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "No such name found"
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

PHONE_PATTERN = re.compile(r'^\d{10}$')

@input_error
def add_contact(args, book):
    name, phone = args
    if not PHONE_PATTERN.match(phone):
        raise ValueError("Invalid phone number format. Please enter a 10-digit number.")
    
    if name not in book:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        record = book[name]
        record.add_phone(phone)
        return "Phone added."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    if not PHONE_PATTERN.match(new_phone):
        raise ValueError("Invalid phone number format. Please enter a 10-digit number.")
    
    if name in book:
        record = book[name]
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def get_phone(args, book):
    name = args[0]
    if name in book:
        return f"Phone for {name}: {book[name].phones[0]}"
    else:
        return "Contact not found."

@input_error
def show_all_contacts(book):
    if not book:
        return "No contacts available."
    else:
        return "\n".join(str(record) for record in book.values())

@input_error
def add_birthday(args, book):
    name, birthday = args
    if name in book:
        book[name].add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    if name in book:
        birthday = book[name].birthday
        return f"Birthday for {name}: {birthday}" if birthday else "Birthday not specified."
    else:
        return "Contact not found."

@input_error
def birthdays(_, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"Upcoming birthday for {name} on {birthday}" for name, birthday in upcoming_birthdays])
    else:
        return "No upcoming birthdays."
    

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():

    book = load_data()
    # book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(_, book))
        else:
            print("Invalid command.")

    save_data(book)

if __name__ == "__main__":
    main()