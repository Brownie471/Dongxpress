import sqlite3
import os

path = os.path.dirname(os.path.abspath(__file__))
file=os.path.join(path, 'library.db')
query='''
INSERT INTO CaiFan_R(CaiName, CaiPrice, Cai, Spicy, In250, Description)
VALUES(?,?,?,?,?,?)
'''
db = sqlite3.connect(file)

while True:
    name = input('name : ')
    if name == 'q':
        break
    price = input('price : ')
    
    spicy = input('is it spicy(T/F) : ')
    if spicy == 'T':
        spicy = True
    else:
        spicy = False
    in250 = input('is it in 250 meal(T/F) : ')
    if in250 == 'T':
        in250 = True
    else:
        in250 = False
    desc = input('Discription : ')

    db.execute(query, [name, price, False, spicy, in250, desc])
    db.commit()
db.close()

