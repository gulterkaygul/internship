from nicegui import ui
from models import User, session, Book, hash_password

# ---------- Yardımcı Fonksiyonlar ----------
def fetch_users():
    users = session.query(User).all()
    return [{'name': u.name, 'password': u.password, 'email': u.email} for u in users]

def fetch_books():
    books = session.query(Book).all()
    return [{'title': b.title, 'status': b.is_borrowed} for b in books]

# ---------- Ana Sayfa ----------
@ui.page('/')
def home():
    with ui.column().classes('w-full items-center justify-center min-h-screen bg-gray-100'):
        ui.label('📚 Library System').classes('text-3xl font-bold mb-6')
        ui.button('🔐 Admin Panel', on_click=lambda: ui.navigate.to('/admin')).classes('mb-4 w-64')
        ui.button('👤 User Panel', on_click=lambda: ui.navigate.to('/user')).classes('w-64')

# ---------- Admin Sayfası ----------
@ui.page('/admin')
def admin_panel():
    with ui.column().classes('w-full items-center justify-center min-h-screen bg-white'):

        ui.label('🔐 Admin Panel').classes('text-2xl font-bold mb-4')

        # USER EKLEME FORMU
        with ui.card().classes('w-96 p-4 mb-4'):
            ui.label('Add User').classes('font-bold mb-2')
            name = ui.input('Name').classes('mb-2')
            email = ui.input('Email').classes('mb-2')
            password = ui.input('Password').classes('mb-2')

            def save_user():
                if name.value and password.value:
                    hashed = hash_password(password.value)
                    session.add(User(name=name.value, email=email.value, password=hashed))
                    session.commit()
                    name.value, email.value, password.value = "", "", ""
                    user_table.rows = fetch_users()
                    user_table.update()
                    ui.notify("User saved")
                else:
                    ui.notify("Fill all fields")

            ui.button('Save User', on_click=save_user).classes('w-full')

        # BOOK EKLEME FORMU
        with ui.card().classes('w-96 p-4 mb-4'):
            book_title = ui.input('Book Title').classes('mb-2')

            def save_book():
                if book_title.value:
                    session.add(Book(title=book_title.value))
                    session.commit()
                    book_title.value = ""
                    book_table.rows = fetch_books()
                    book_table.update()
                    ui.notify("Book saved")
                else:
                    ui.notify("Enter a book title")

            ui.button('Add Book', on_click=save_book).classes('w-full')

        # USER TABLE
        with ui.card().classes('w-full max-w-screen-md p-4 mb-4'):
            ui.label('Users Table').classes('font-bold mb-2')
            global user_table
            user_table = ui.table(columns=[
                {'label': 'Name', 'field': 'name'},
                {'label': 'Password', 'field': 'password'},
                {'label': 'Email', 'field': 'email'},
            ], rows=fetch_users()).classes('w-full')

        # BOOK TABLE
        with ui.card().classes('w-full max-w-screen-md p-4'):
            ui.label('Books Table').classes('font-bold mb-2')
            global book_table
            book_table = ui.table(columns=[
                {'label': 'Title', 'field': 'title'},
                {'label': 'Status', 'field': 'status'},
            ], rows=fetch_books()).classes('w-full')

# ---------- User Sayfası ----------
@ui.page('/user')
def user_panel():
    with ui.column().classes('w-full items-center justify-center min-h-screen bg-gray-50'):
        ui.label('👤 Welcome User').classes('text-2xl font-bold mb-4')
        ui.label('This is your user dashboard.').classes('text-gray-600')

# ---------- Uygulama Başlat ----------
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Library System")