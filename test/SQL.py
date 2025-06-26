from nicegui import ui
from models import User, session  # Modeli bu şekilde çağırıyoruz

# Form giriş alanları
name = ui.input('Name')
password = ui.input('Password', password=True)
email = ui.input('Email')
ui.button('Save', on_click=lambda: save_user())

# Tablo sütunları
columns = [
    {'label': 'Name', 'field': 'name'},
    {'label': 'Password', 'field': 'password'},
    {'label': 'Email', 'field': 'email'}
]

# Kullanıcıları veritabanından çek
def fetch_users():
    users = session.query(User).all()
    return [
        {
            'name': user.name,
            'password': '*' * len(user.password),
            'email': user.email
        }
        for user in users
    ]

# Kaydetme işlemi
def save_user():
    if name.value and password.value:
        new_user = User(name=name.value, password=password.value, email=email.value)
        session.add(new_user)
        session.commit()
        name.value = ""
        password.value = ""
        email.value = ""
        table.rows = fetch_users()
        table.update()
    else:
        ui.notify('Please fill all the blanks')

# Tabloyu oluştur
table = ui.table(columns=columns, rows=fetch_users())

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
