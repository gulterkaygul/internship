from nicegui import ui
from models import User, session, Book, hash_password, verify_password

current_user = {'user': None}

def fetch_users():
    users = session.query(User).all()
    return [{'id': u.id, 'name': u.name, 'email': u.email} for u in users]

def fetch_books():
    books = session.query(Book).all()
    return [{'id': b.id, 'title': b.title, 'status': 'Borrowed' if b.is_borrowed else 'Available'} for b in books]

def require_login():
    if not current_user['user']:
        ui.navigate.to('/login')
        return False
    return True

@ui.page('/login')
def login_page():
    with ui.column().classes('w-full items-center justify-center min-h-screen bg-gray-100'):
        ui.label('🔐 Login').classes('text-3xl font-bold mb-6')

        email_input = ui.input('Email').classes('mb-2')
        password_input = ui.input('Password', password=True).classes('mb-4')

        def do_login():
            user = session.query(User).filter_by(email=email_input.value).first()
            if user and verify_password(password_input.value, user.password):
                current_user['user'] = user
                ui.notify(f'Welcome {user.name}!')
                if user.role == 'admin':
                    ui.navigate.to('/admin')
                else:
                    ui.navigate.to('/user')
            else:
                ui.notify('Invalid email or password', color='red')

        ui.button('Login', on_click=do_login).classes('w-64')

@ui.page('/')
def home():
    if current_user['user']:
        if current_user['user'].role == 'admin':
            ui.navigate.to('/admin')
        else:
            ui.navigate.to('/user')
    else:
        ui.navigate.to('/login')

@ui.page('/admin')
def admin_panel():
    if not require_login():
        return
    if current_user['user'].role != 'admin':
        ui.notify("Unauthorized access", color='red')
        ui.navigate.to('/login')
        return

    global user_table, book_table

    with ui.column().classes('w-full items-center justify-center min-h-screen bg-white'):
        ui.label('🔐 Admin Panel').classes('text-2xl font-bold mb-4')

        # Kullanıcı Ekleme
        with ui.card().classes('w-96 p-4 mb-4'):
            ui.label('Add User').classes('font-bold mb-2')
            name = ui.input('Name').classes('mb-2')
            email = ui.input('Email').classes('mb-2')
            password = ui.input('Password').classes('mb-2')

            def save_user():
                try:
                    if name.value and password.value and email.value:
                        hashed = hash_password(password.value)
                        session.add(User(name=name.value, email=email.value, password=hashed))
                        session.commit()
                        name.value, email.value, password.value = "", "", ""
                        user_table.rows = fetch_users()
                        user_table.update()
                        ui.notify("User saved")
                    else:
                        ui.notify("Fill all fields", color='red')
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error: {e}", color='red')

            ui.button('Save User', on_click=save_user).classes('w-full')

        # Kullanıcı Tablosu (Silme işlemi için)
        with ui.card().classes('w-full max-w-screen-md p-4 mb-4'):
            ui.label('Users Table').classes('font-bold mb-2')
            user_table = ui.table(
                columns=[
                    {'label': 'ID', 'field': 'id'},
                    {'label': 'Name', 'field': 'name'},
                    {'label': 'Email', 'field': 'email'},
                ],
                rows=fetch_users(),
                row_key='id',
                #multiple=True
            )

            def delete_selected_users():
                selected_ids = [row['id'] for row in user_table.get_selected_rows()]
                if not selected_ids:
                    ui.notify("Select user(s) to delete", color='red')
                    return
                try:
                    for uid in selected_ids:
                        user = session.query(User).get(uid)
                        if user:
                            session.delete(user)
                    session.commit()
                    user_table.rows = fetch_users()
                    user_table.update()
                    ui.notify("Selected users deleted")
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error: {e}", color='red')

            ui.button('Delete Selected Users', on_click=delete_selected_users).classes('mt-2')

        # Kitap Ekleme
        with ui.card().classes('w-96 p-4 mb-4'):
            book_title = ui.input('Book Title').classes('mb-2')

            def save_book():
                try:
                    if book_title.value:
                        session.add(Book(title=book_title.value))
                        session.commit()
                        book_title.value = ""
                        book_table.rows = fetch_books()
                        book_table.update()
                        ui.notify("Book saved")
                    else:
                        ui.notify("Enter a book title", color='red')
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error: {e}", color='red')

            ui.button('Add Book', on_click=save_book).classes('w-full')

        # Kitap Tablosu (Silme işlemi için)
        with ui.card().classes('w-full max-w-screen-md p-4'):
            ui.label('Books Table').classes('font-bold mb-2')
            book_table = ui.table(
                columns=[
                    {'label': 'ID', 'field': 'id'},
                    {'label': 'Title', 'field': 'title'},
                    {'label': 'Status', 'field': 'status'},
                ],
                rows=fetch_books(),
                row_key='id',
                #multiple=True
            )

            def delete_selected_books():
                selected_ids = [row['id'] for row in book_table.get_selected_rows()]
                if not selected_ids:
                    ui.notify("Select book(s) to delete", color='red')
                    return
                try:
                    for bid in selected_ids:
                        book = session.query(Book).get(bid)
                        if book:
                            session.delete(book)
                    session.commit()
                    book_table.rows = fetch_books()
                    book_table.update()
                    ui.notify("Selected books deleted")
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error: {e}", color='red')

            ui.button('Delete Selected Books', on_click=delete_selected_books).classes('mt-2')

@ui.page('/user')
def user_panel():
    if not require_login():
        return
    if current_user['user'].role != 'user':
        ui.notify("Unauthorized access", color='red')
        ui.navigate.to('/login')
        return

    with ui.column().classes('w-full items-center justify-center min-h-screen bg-gray-50'):
        ui.label(f'👤 Welcome {current_user["user"].name}').classes('text-2xl font-bold mb-4')

        with ui.card().classes('w-full max-w-screen-md p-4'):
            ui.label('Books Table').classes('font-bold mb-2')
            books = fetch_books()
            ui.table(columns=[
                {'label': 'Title', 'field': 'title'},
                {'label': 'Status', 'field': 'status'},
            ], rows=books).classes('w-full')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Library System")

