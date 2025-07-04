from nicegui import ui
from models import User, session, Book, hash_password, verify_password

# Global current_user tanımı
current_user = {'user': None}

def fetch_users():
    users = session.query(User).all()
    return [{'id': u.id, 'name': u.name, 'email': u.email, 'password': u.password} for u in users]

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
    with ui.column().style('''
        background-image: url('/static/background.jpg');
        background-size: cover;
        background-position: center;
        min-height: 100vh;
    ''').classes('w-full items-center justify-center'):

        # Logo
        ui.image('/static/logo.png').classes('w-24 h-24 mb-4')

        with ui.card().classes('p-10 bg-white/30 backdrop-blur-md rounded-xl shadow-lg'):

            ui.label('🔐 Login').classes('text-3xl font-bold mb-6 text-indigo-800')

            email_input = ui.input('Email').props('outlined dense').classes('mb-4 w-80')
            password_input = ui.input('Password', password=True).props('outlined dense').classes('mb-4 w-80')

            def do_login():
                user = session.query(User).filter_by(email=email_input.value).first()
                if user and verify_password(password_input.value, user.password):
                    current_user['user'] = user
                    ui.notify(f'Welcome, {user.name}!', color='green')
                    if user.role == 'admin':
                        ui.navigate.to('/admin')
                    else:
                        ui.navigate.to('/user')
                else:
                    ui.notify('Invalid email or password!', color='red')

            ui.button('Login', on_click=do_login).classes(
                'bg-indigo-600 hover:bg-indigo-700 text-white w-full mt-2 rounded-lg text-lg'
            )

            ui.link('Don’t have an account? Register', '/register').classes('text-sm mt-4 text-center')
            ui.link('Forgot your password?', '/forgot').classes('text-sm mt-1 text-center')

@ui.page('/register')
def register_page():
    with ui.column().style('''
        background-image: url('/static/background.jpg');
        background-size: cover;
        background-position: center;
        min-height: 100vh;
    ''').classes('w-full items-center justify-center'):

        ui.image('/static/logo.png').classes('w-24 h-24 mb-4')

        with ui.card().classes('p-10 bg-white/30 backdrop-blur-md rounded-xl shadow-lg'):

            ui.label('📝 Create Account').classes('text-2xl font-bold mb-6 text-indigo-800')

            name_input = ui.input('Full Name').props('outlined dense').classes('mb-4 w-80')
            email_input = ui.input('Email').props('outlined dense').classes('mb-4 w-80')
            password_input = ui.input('Password', password=True).props('outlined dense').classes('mb-4 w-80')

            def do_register():
                if not (name_input.value and email_input.value and password_input.value):
                    ui.notify('Please fill out all fields.', color='red')
                    return
                if session.query(User).filter_by(email=email_input.value).first():
                    ui.notify('Email already registered.', color='orange')
                    return

                new_user = User(
                    name=name_input.value,
                    email=email_input.value,
                    password=hash_password(password_input.value),
                    role='user'  # default role
                )
                session.add(new_user)
                session.commit()
                ui.notify('Account created successfully! Please log in.', color='green')
                ui.navigate.to('/login')

            ui.button('Register', on_click=do_register).classes(
                'bg-green-600 hover:bg-green-700 text-white w-full mt-2 rounded-lg text-lg'
            )

            ui.link('Already have an account? Login', '/login').classes('text-sm mt-4 text-center')

@ui.page('/forgot')
def forgot_password_page():
    with ui.column().style('''
        background-image: url('/static/background.jpg');
        background-size: cover;
        background-position: center;
        min-height: 100vh;
    ''').classes('w-full items-center justify-center'):

        ui.image('/static/logo.png').classes('w-24 h-24 mb-4')

        with ui.card().classes('p-10 bg-white/30 backdrop-blur-md rounded-xl shadow-lg'):

            ui.label('🔑 Forgot Password').classes('text-2xl font-bold mb-6 text-indigo-800')

            email_input = ui.input('Enter your registered email').props('outlined dense').classes('mb-4 w-80')

            def send_reset_email():
                user = session.query(User).filter_by(email=email_input.value).first()
                if user:
                    # Gerçek e-posta sistemi entegrasyonu yapılabilir
                    ui.notify('A reset link has been sent to your email address.', color='green')
                else:
                    ui.notify('No account found with this email.', color='red')

            ui.button('Send Reset Link', on_click=send_reset_email).classes(
                'bg-blue-600 hover:bg-blue-700 text-white w-full mt-2 rounded-lg text-lg'
            )

            ui.link('Back to Login', '/login').classes('text-sm mt-4 text-center')

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
                        # Email kayıtlı mı kontrolü
                        if session.query(User).filter_by(email=email.value).first():
                            ui.notify("Email already registered.", color="orange")
                            return
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
                    {'label': 'Password', 'field': 'password'},
                ],
                rows=fetch_users(),
                row_key='id',
                selection='multiple'  # Çoklu seçim aktif
            )

            def delete_selected_users():
                selected_ids = [row['id'] for row in user_table.selected]
                if not selected_ids:
                    ui.notify("Select user(s) to delete", color='red')
                    return
                try:
                    for uid in selected_ids:
                        user = session.get(User, uid)
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
                selection='multiple'  # Çoklu seçim aktif
            )

            def delete_selected_books():
                selected_ids = [row['id'] for row in book_table.selected]
                if not selected_ids:
                    ui.notify("Select book(s) to delete", color='red')
                    return
                try:
                    for bid in selected_ids:
                        book = session.get(Book, bid)
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
