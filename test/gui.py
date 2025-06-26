from nicegui import ui

name= ui.input('Name')
password = ui.input('Password' , password = True) #input alani gizli olur

save = ui.button('Save' , on_click = lambda:save())

columns = [
    {'label': 'Name', 'field' : 'name' },
    {'label': 'Password', 'field' : 'password' }
]

rows = []

def save():
    new_dict = {'name':f'{name.value}', 'password': '*' * len(password.value)}
    rows.append(new_dict)
    table.update()
    name.value = "" #saving name and password with empty strings
    password.value = ""

table = ui.table(columns = columns , rows = rows)

ui.run()