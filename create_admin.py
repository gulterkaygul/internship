from models import Admin, session, hash_password

admin = Admin(username='admin', password=hash_password('123'))
session.add(admin)
session.commit()

print("Admin user created.")