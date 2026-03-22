import json
from datetime import date, timedelta

# This is book class
class Book:
    def __init__(self, title, author, book_id):
        self.title = title
        self.author = author
        self.book_id = book_id
        self.available = True
        self.borrow_date = None
        self.due_date = None

    def display_info(self):
        status = "Available" if self.available else "Borrowed"
        info = f"{self.book_id} | {self.title} | {self.author} | {status}"
        if not self.available and self.due_date:
            info += f" | Due: {self.due_date}"
        print(info)

    def mark_borrowed(self):
        self.available = False
        self.borrow_date = date.today()
        self.due_date = self.borrow_date + timedelta(days=7)

    def mark_returned(self):
        self.available = True
        self.borrow_date = None
        self.due_date = None


# ---------------- USER ----------------
class User:
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.borrowed_books = []
        self.fine = 0.0

    def borrow_book(self, book):
        if len(self.borrowed_books) >= 3:
            print("Error: Cannot borrow more than 3 books")
            return False
        self.borrowed_books.append(book)
        return True

    def return_book(self, book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            return True
        else:
            print("Error: You did not borrow this book")
            return False

    def display_user_info(self):
        print(f"ID: {self.user_id} | Name: {self.name} | Fine: ${self.fine:.2f}")
        print("Borrowed books:")
        if not self.borrowed_books:
            print("  None")
        else:
            today = date.today()
            for b in self.borrowed_books:
                overdue = " (OVERDUE)" if b.due_date and b.due_date < today else ""
                print(f"  - {b.title} (due: {b.due_date}){overdue}")


# ---------------- ADMIN ----------------
class Admin:
    def __init__(self, password="admin123"):
        self.password = password

    def login(self):
        pwd = input("Admin password: ")
        return pwd == self.password

    def add_book(self, library):
        title = input("Enter title: ").strip()
        author = input("Enter author: ").strip()
        book_id = input("Enter book ID: ").strip()

        if not title or not author or not book_id:
            print("Error: Invalid input")
            return

        if library.find_book(book_id):
            print("Error: Book ID already exists")
            return

        library.add_book(Book(title, author, book_id))
        print("Book added successfully")

    def remove_book(self, library):
        book_id = input("Enter book ID to remove: ").strip()
        book = library.find_book(book_id)
        if not book:
            print("Error: Book not found")
            return
        if not book.available:
            print("Error: Cannot remove a borrowed book")
            return
        library.remove_book(book)
        print("Book removed successfully")


# ---------------- LIBRARY ----------------
class Library:
    def __init__(self):
        self.list_of_books = []
        self.list_of_users = []
        self.load_data()

    # -------- SAVE DATA --------
    def save_data(self):
        books_data = []
        for b in self.list_of_books:
            books_data.append({
                "title": b.title,
                "author": b.author,
                "book_id": b.book_id,
                "available": b.available,
                "borrow_date": b.borrow_date.isoformat() if b.borrow_date else None,
                "due_date": b.due_date.isoformat() if b.due_date else None
            })

        users_data = []
        for u in self.list_of_users:
            users_data.append({
                "name": u.name,
                "user_id": u.user_id,
                "borrowed_books": [b.book_id for b in u.borrowed_books],
                "fine": u.fine
            })

        with open("books.json", "w") as f:
            json.dump(books_data, f, indent=4)

        with open("users.json", "w") as f:
            json.dump(users_data, f, indent=4)

    # -------- LOAD DATA --------
    def load_data(self):
        # Load books
        try:
            with open("books.json", "r") as f:
                books = json.load(f)
                for b in books:
                    book = Book(b["title"], b["author"], b["book_id"])
                    book.available = b["available"]
                    if b["borrow_date"]:
                        book.borrow_date = date.fromisoformat(b["borrow_date"])
                    if b["due_date"]:
                        book.due_date = date.fromisoformat(b["due_date"])
                    self.list_of_books.append(book)
        except FileNotFoundError:
            print("No existing books.json. Starting fresh.")
        except Exception as e:
            print(f"Error loading books: {e}")

        # Load users
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
                for u in users:
                    user = User(u["name"], u["user_id"])
                    user.fine = u.get("fine", 0.0)
                    for book_id in u["borrowed_books"]:
                        book = self.find_book(book_id)
                        if book:
                            user.borrowed_books.append(book)
                    self.list_of_users.append(user)
        except FileNotFoundError:
            print("No existing users.json. Starting fresh.")
        except Exception as e:
            print(f"Error loading users: {e}")

    # -------- ADD BOOK --------
    def add_book(self, book):
        self.list_of_books.append(book)

    # -------- REMOVE BOOK --------
    def remove_book(self, book):
        self.list_of_books.remove(book)

    # -------- REGISTER USER --------
    def register_user(self):
        name = input("Enter name: ").strip()
        user_id = input("Enter user ID: ").strip()

        if not name or not user_id:
            print("Error: Invalid input")
            return

        if self.find_user(user_id):
            print("Error: User ID already exists")
            return

        self.list_of_users.append(User(name, user_id))
        print("User registered successfully")

    # -------- FIND HELPERS --------
    def find_book(self, book_id):
        for b in self.list_of_books:
            if b.book_id == book_id:
                return b
        return None

    def find_user(self, user_id):
        for u in self.list_of_users:
            if u.user_id == user_id:
                return u
        return None

    # -------- BORROW --------
    def lend_book(self):
        book_id = input("Enter book ID: ").strip()
        user_id = input("Enter user ID: ").strip()

        book = self.find_book(book_id)
        user = self.find_user(user_id)

        if not book or not user:
            print("Error: User or Book not found")
            return

        if not book.available:
            print("Error: Book not available")
            return

        if user.borrow_book(book):
            book.mark_borrowed()
            print(f"Book borrowed successfully. Due date: {book.due_date}")

    # -------- RETURN --------
    def accept_return(self):
        book_id = input("Enter book ID: ").strip()
        user_id = input("Enter user ID: ").strip()

        book = self.find_book(book_id)
        user = self.find_user(user_id)

        if not book or not user:
            print("Error: Not found")
            return

        if user.return_book(book):
            # Calculate fine if overdue
            today = date.today()
            if book.due_date and book.due_date < today:
                days_late = (today - book.due_date).days
                fine = days_late * 2  # $2 per day
                user.fine += fine
                print(f"Late return! Overdue by {days_late} day(s). Fine added: ${fine:.2f}")
                print(f"Total fine now: ${user.fine:.2f}")
            else:
                print("Returned on time")

            book.mark_returned()
            print("Book returned successfully")

    # -------- SEARCH (partial match) --------
    def search_book_by_title(self):
        title = input("Enter title (or part): ").strip().lower()
        found = False
        for b in self.list_of_books:
            if title in b.title.lower():
                b.display_info()
                found = True
        if not found:
            print("No book found matching that title")

    # -------- SORTED DISPLAY --------
    def show_all_books(self):
        if not self.list_of_books:
            print("No books in library.")
            return
        sorted_books = sorted(self.list_of_books, key=lambda b: b.title.lower())
        for b in sorted_books:
            b.display_info()

    # -------- ADMIN-ONLY VIEWS --------
    def show_all_users(self):
        if not self.list_of_users:
            print("No users registered.")
            return
        for u in self.list_of_users:
            u.display_user_info()
            print()

    def show_overdue_books(self):
        today = date.today()
        found = False
        for u in self.list_of_users:
            for b in u.borrowed_books:
                if b.due_date and b.due_date < today:
                    print(f"Overdue: '{b.title}' (ID {b.book_id}) borrowed by {u.name} – due {b.due_date}")
                    found = True
        if not found:
            print("No overdue books.")


# ---------------- MAIN ----------------
def main():
    library = Library()
    admin = Admin()

    while True:
        print("\n===== LIBRARY SYSTEM =====")
        print("1. Admin Login")
        print("2. User Login")
        print("3. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            if not admin.login():
                print("Wrong password.")
                continue

            # Admin menu
            while True:
                print("\n--- Admin Menu ---")
                print("1. Add Book")
                print("2. Remove Book")
                print("3. Register User")
                print("4. Show All Books")
                print("5. Show All Users (with fines)")
                print("6. Show Overdue Books")
                print("7. Save & Exit to Main Menu")
                admin_choice = input("Choose: ").strip()

                if admin_choice == "1":
                    admin.add_book(library)
                elif admin_choice == "2":
                    admin.remove_book(library)
                elif admin_choice == "3":
                    library.register_user()
                elif admin_choice == "4":
                    library.show_all_books()
                elif admin_choice == "5":
                    library.show_all_users()
                elif admin_choice == "6":
                    library.show_overdue_books()
                elif admin_choice == "7":
                    library.save_data()
                    break
                else:
                    print("Invalid option")

        elif choice == "2":
            user_id = input("Enter your User ID: ").strip()
            user = library.find_user(user_id)
            if not user:
                print("User not found. Please ask admin to register you.")
                continue

            print(f"Welcome, {user.name}!")
            # Show any overdue warnings immediately
            today = date.today()
            for b in user.borrowed_books:
                if b.due_date and b.due_date < today:
                    print(f"WARNING: Your book '{b.title}' is overdue (due {b.due_date})!")

            while True:
                print("\n--- User Menu ---")
                print("1. Borrow Book")
                print("2. Return Book")
                print("3. Search Book")
                print("4. Show All Books")
                print("5. Show My Info")
                print("6. Logout")
                user_choice = input("Choose: ").strip()

                if user_choice == "1":
                    library.lend_book()
                elif user_choice == "2":
                    library.accept_return()
                elif user_choice == "3":
                    library.search_book_by_title()
                elif user_choice == "4":
                    library.show_all_books()
                elif user_choice == "5":
                    user.display_user_info()
                elif user_choice == "6":
                    break
                else:
                    print("Invalid option")

        elif choice == "3":
            print("Goodbye!")
            library.save_data()
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()