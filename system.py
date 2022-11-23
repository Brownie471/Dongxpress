from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)
#-----------------------------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('templates/index.html')
#-----------------------------------------------------------------------------------------------
@app.route('/people/')
def people():
    return render_template('templates/people.html')

#rationale -----------------------------------------------------------------------------------------------
@app.route('/rationale/')
def rationale():
    return render_template('templates/rationale.html')

#login-----------------------------------------------------------------------------------------------
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)
        

        query_delete = '''
            DELETE FROM Logined
            '''

        db.execute(query_delete)
            
        db.commit()
        db.close()
        return render_template('templates/login.html')
    else:
        name = request.form['uname']
        password = request.form['pw']

        #print(name, password)

        if (len(name) == 0 and len(password) == 0) or len(name) == 0:
            return render_template('templates/login_fail_noentry.html')
        elif len(password) == 0:
            return render_template('templates/login_fail_noentry_nopw.html', name=name)

        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)
        query_checkpw = '''
SELECT * FROM Customer_Account WHERE Customer_Account.Name = ? AND Customer_Account.Password = ?        
        '''
        query = '''
SELECT * FROM Customer_Account        
        '''
        cursor = db.execute(query)
        #print(cursor.fetchall())

        cursor = db.execute(query_checkpw, [name, password])
        result = cursor.fetchall()
        #print(result)
        
        if len(result) == 0:
            db.close()
            return render_template('templates/login_fail_wrongpw.html', name = name)
        else:
            result = result[0]
            query_login = '''
            INSERT INTO Logined(Name, Class, IndexNo, Password) VALUES(?,?,?,?)
            '''

            query_delete = '''
            DELETE FROM Logined
            '''

            db.execute(query_delete)
            db.execute(query_login, [result[0], result[1], result[2], result[3]])
            print('done')
            db.commit()
            db.close()
            return render_template('templates/account_home.html', name = result[0], class_ = result[1], indexno = result[2])

#password change#-----------------------------------------------------------------------------------------------
@app.route('/changepw/', methods=['GET','POST'])
def changepw():
    if request.method == 'GET':
        return render_template('templates/account_changepw.html')
    else:
        curr_pw = request.form['curr']
        new_pw = request.form['new']

        print(curr_pw, new_pw)

        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db  = sqlite3.connect(file)
        query_get_corr_pw = '''
        SELECT Password FROM Logined
        '''
        cursor = db.execute(query_get_corr_pw)
        correct_pw = cursor.fetchone()[0]
        print(correct_pw)
        if curr_pw != correct_pw:
            db.close()
            return render_template('templates/account_changepw_failwrongpw.html')
        else:
            query_update_pw_logined = '''
            UPDATE Logined SET Password = ? 
            '''

            query_get_class_index = '''
            SELECT * FROM Logined
            '''

            query_update_pw_general = '''
            UPDATE Customer_Account SET Password = ? WHERE Class = ? AND IndexNo = ?
            '''
            db.execute(query_update_pw_logined, [new_pw])

            cursor = db.execute(query_get_class_index)
            result = cursor.fetchone()
            class_, index_no = result[1], result[2]

            db.execute(query_update_pw_general, [new_pw, class_, index_no])
            db.commit()
            db.close()
            return render_template('templates/account_changepw_success.html')


    


#confirm password and password for registration#-----------------------------------------------------------------------------------------------
@app.route('/register/', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('templates/register.html')
    else:
        name = request.form['name']
        class_ = request.form['class_']
        index_no = request.form['indexno']

        pw1 = request.form['pw1']
        pw2 = request.form['pw2']

        if pw1 != pw2:
            return render_template('templates/register_failpw.html', name = name, class_ = class_, index_no = index_no)
        elif len(name) == 0 or len(class_) == 0 or len(index_no) == 0 or len(pw1) == 0:
            return render_template('templates/register_failempty.html', name = name, class_ = class_, index_no = index_no)

        else:
            query_check = '''
            SELECT * FROM Customer_Account WHERE Class = ? AND IndexNo = ?
            '''
            query_register = '''
            INSERT INTO Customer_Account(Name, Class, IndexNo, Password) VALUES(?,?,?,?) 
            '''

            path = os.path.dirname(os.path.abspath(__file__))
            file = os.path.join(path, 'library.db')

            db = sqlite3.connect(file)
            cursor = db.execute(query_check, [class_, index_no])
            if len(cursor.fetchall()) > 0:
                db.close()
                return render_template('templates/register_failexist.html')


            db.execute(query_register, [name, class_, index_no, pw1])
            db.commit()

            
            db.close()
            return render_template('templates/register_successful.html')
            
#-----------------------------------------------------------------------------------------------
@app.route('/owner_login/', methods = ['GET', 'POST'])
def owner_login():
    if request.method =='GET':
        return render_template('templates/login_owner.html', incorrect = '')
    else:
        p1 = request.form['pw']
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)
        query = '''
        SELECT * FROM Owner
        '''
        cursor = db.execute(query)
        correct = cursor.fetchone()[0]
        if str(correct) == str(p1):
            path = os.path.dirname(os.path.abspath(__file__))
            file = os.path.join(path, 'library.db')

            db = sqlite3.connect(file)
            query_get_all_250 = '''
            SELECT * FROM Pending_Delivery_250 
ORDER BY Delivery_Date ASC
            '''
            cursor = db.execute(query_get_all_250)
            result_250 = cursor.fetchall()

            query_get_all_cust = '''
            SELECT * FROM Pending_Delivery_Cust 
ORDER BY Delivery_Date ASC
            '''
            cursor = db.execute(query_get_all_cust)
            result_cust = cursor.fetchall()
            ultra_final = []
            for row in result_cust:
                final = []
                #final_temp = []
                orders = row[-1]
                
                #row = row[:len(row) - 1]
                orders = orders.split('\n')
                #print(orders)
                #print(len(row))
                for item_index in range(len(row)):
                    #print(item_index)
                    if item_index == 4:
                        print('==-===============================================================================')
                        final.append(str(round(row[item_index], 2)))
                    elif item_index != len(row) - 1:
                        final.append(row[item_index])
                    
                    else:
                        orders_split = []
                        all_names = []
                        all_quant = []
                        for row_ in range(len(orders)-1):
                        
                            #print(orders[row_].split('='))
                            all_names.append(str(orders[row_].split('=')[0]))
                            #all_names += "\n"
                            all_quant.append(str(orders[row_].split('=')[1]))
                            #all_quant += "\n"
                            #print(all_names)
                            
                        final.append(all_names)
                        final.append(all_quant)
                        #print(final_temp)
                
                ultra_final.append(final)
            #print(ultra_final)
                
                



            db.close()

            return render_template('templates/result_owner.html', result_250 = result_250, result_cust = ultra_final)

        else:
            return render_template('templates/login_owner.html', incorrect = '*The entered password is incorrect*')


#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
@app.route('/account/')
def account():
    return render_template('templates/account.html')
#-----------------------------------------------------------------------------------------------
@app.route('/account_home/')
def account_home():
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')

    db = sqlite3.connect(file)

    query_get_name = '''
    SELECT Name FROM Logined
    '''

    query_delete_sc = '''
    DELETE FROM Shopping_Cart
    '''

    query_delete_log = '''
    DELETE FROM Action_sc
    '''

    cursor = db.execute(query_get_name)
    db.execute(query_delete_sc)
    db.execute(query_delete_log)
    db.commit()
    name = cursor.fetchone()[0]

    db.close()
    return render_template('templates/account_home.html', name=name)

#-----------------------------------------------------------------------------------------------
@app.route('/order250/', methods=['GET', 'POST'])
def order250():
    if request.method == 'GET':
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')
        db = sqlite3.connect(file)

        query_get250_cai = '''
        SELECT CaiID, CaiName, CaiPrice, Spicy, Description 
        FROM Caifan_C 
        WHERE CaiFan_C.In250 = 1
        AND CaiFan_C.Cai = 1
        '''

        cursor = db.execute(query_get250_cai)
        cai = cursor.fetchall()

        query_get250_not_cai = '''
        SELECT CaiID, CaiName, CaiPrice, Spicy, Description 
        FROM Caifan_R 
        WHERE CaiFan_R.In250 = 1 
        AND CaiFan_R.Cai = 0
        '''

        cursor = db.execute(query_get250_not_cai)
        not_cai = cursor.fetchall()
        db.close()
        #print(cai)
        return render_template('templates/order_250.html', cai = cai, not_cai = not_cai)
    else:
        cai1_id = request.form['cai1']
        cai2_id = request.form['cai2']
        rou1_id = request.form['rou1']

        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)

        query_get_name_c = '''
        SELECT CaiFan_C.CaiName FROM CaiFan_C WHERE CaiFan_C.CaiID = ?
        '''

        cursor = db.execute(query_get_name_c, [cai1_id])
        cai_1_name = cursor.fetchone()[0]

        cursor = db.execute(query_get_name_c, [cai2_id])
        cai_2_name = cursor.fetchone()[0]

        query_get_name_r = '''
        SELECT CaiFan_R.CaiName FROM CaiFan_R WHERE CaiFan_R.CaiID = ?
        '''

        cursor = db.execute(query_get_name_r, [rou1_id])
        rou_1_name = cursor.fetchone()[0]

        query_delete = "DELETE FROM 'ORDER'"
        

        query_insert_order = "INSERT INTO 'ORDER'(CaiID, CaiName) VALUES(?,?)"
        
        db.execute(query_delete)
        db.commit()
        db.execute(query_insert_order, [cai1_id, cai_1_name])
        db.execute(query_insert_order, [cai2_id, cai_2_name])
        db.execute(query_insert_order, [rou1_id, rou_1_name])
        db.commit()

        query_get_all = "SELECT * FROM 'ORDER'"
        
        cursor = db.execute(query_get_all)
        result = cursor.fetchall()

        db.close()
        from datetime import date
        date_time = date.today()
        print(date_time) 

        date_time = str(date_time).split('-')
        print(date_time) 
        day = int(date_time[2]) 
        month = int(date_time[1])
        year = int(date_time[0])

        if day < 29:
            day += 2
            actual = str(year) + '-' + str(month)+ '-' + str(day)

            print(actual)
            return render_template('templates/order_comfirm250.html', result = result, date_ = actual)
        elif month != 12:
            month += 1
            day = 1
            actual = str(year) + '-' + str(month)+ '-' + str(day)
            print(actual)
            return render_template('templates/order_comfirm250.html', result = result, date_ = actual)
        else:
            month = 1
            day = 1
            year += 1
            actual = str(year) + '-' + str(month)+ '-' + str(day)
            print(actual)
            return render_template('templates/order_comfirm250.html', result = result, date_ = actual)
#-----------------------------------------------------------------------------------------------
@app.route('/thank_250/', methods=['POST'])
def thank_250():
    query_get_user = '''
    SELECT Logined.Name, Logined.Class, Logined.IndexNo
    FROM Logined
    '''

    query_get_order = "SELECT 'ORDER'.CaiName FROM 'ORDER'"


    delivery_date = request.form['ddate']

    query_insert = "INSERT INTO Pending_Delivery_250(Name, 'Class', IndexNo, Cai1, Cai2, Rou, Delivery_Date, Cost) VALUES(?,?,?,?,?,?,?,?)"

    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')

    db = sqlite3.connect(file)

    cursor = db.execute(query_get_order)
    
    result = cursor.fetchall()
    print(result)
    #cai1 = cursor.fetchall()[0]#[0]
    #cai2 = cursor.fetchall()[1]#[0]
    #rou = cursor.fetchall()[2]#[0]
    cai1, cai2, rou = result[0][0], result[1][0], result[2][0]

    cursor = db.execute(query_get_user)
    result = cursor.fetchone()
    print(result)
    name, class_, indexno = result[0], result[1], result[2]

    cost = '2.50'
    try:
        db.execute(query_insert, [name, class_, indexno, cai1, cai2, rou, delivery_date, cost])
        
        try:
            query_insert_t = "INSERT INTO Pending_Delivery_Cust(Name, 'Class', IndexNo, Delivery_Date, Cost, All_cai) VALUES(?,?,?,?,?,?)"
            db.execute(query_insert_t, [name, class_, indexno, delivery_date, 0.0, '-'])
            db.close()

            db = sqlite3.connect(file)
            db.execute(query_insert, [name, class_, indexno, cai1, cai2, rou, delivery_date, cost])
            db.commit()
            db.close()

            return render_template('thank.html')
        except sqlite3.IntegrityError:
            db.close()
            return render_template('templates/order_too_many.html', type_ = 'custom order')

    except sqlite3.IntegrityError:
        

        db.close()
        return render_template('templates/order_too_many.html', type_ = '$2.50 meal')


#-----------------------------------------------------------------------------------------------
@app.route('/order_cust/', methods = ['GET', 'POST'])
def order_cust():
    if request.method == 'GET':
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)

        query_delete_cart = '''
        DELETE FROM Shopping_Cart
        '''

        query_get_all_c = '''
            SELECT * FROM CaiFan_C
        '''
        query_get_all_r = '''
            SELECT * FROM CaiFan_R
        '''

        cursor = db.execute(query_get_all_c)
        all_cai = cursor.fetchall()
        cursor = db.execute(query_get_all_r)
        all_rou = cursor.fetchall()

        #db.execute(query_delete_cart)
        db.commit()

        db.close()

        return render_template('templates/order_cust.html', cai=all_cai, rou=all_rou)
    else:
        query_get_user = '''
        SELECT Logined.Name, Logined.Class, Logined.IndexNo
        FROM Logined
        '''

        query_get_order = "SELECT * FROM Shopping_Cart"


        delivery_date = request.form['ddate']

        query_insert = "INSERT INTO Pending_Delivery_Cust(Name, 'Class', IndexNo, Delivery_Date, Cost, All_cai) VALUES(?,?,?,?,?,?)"

        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path, 'library.db')

        db = sqlite3.connect(file)

        cursor = db.execute(query_get_order)
        
        result = cursor.fetchall()
        print(result)
        #cai1 = cursor.fetchall()[0]#[0]
        #cai2 = cursor.fetchall()[1]#[0]
        #rou = cursor.fetchall()[2]#[0]
        all = ""
        cost =1.0
        for row in result:
            cost += float(row[1]) *  int(row[2])
            all += str(row[0]) + '=' + str(row[2])
            all += '\n'

        cursor = db.execute(query_get_user)
        result = cursor.fetchone()
        print(result)
        name, class_, indexno = result[0], result[1], result[2]

        
        
        try:
            db.execute(query_insert, [name, class_, indexno, delivery_date, cost, all])
            
            try:
                query_insert_t = "INSERT INTO Pending_Delivery_250(Name, 'Class', IndexNo, Cai1, Cai2, Rou, Delivery_Date, Cost) VALUES(?,?,?,?,?,?,?,?)"
                db.execute(query_insert_t, [name, class_, indexno, '-', '-', '-', delivery_date, 0.0])
                db.close()
                db = sqlite3.connect(file)
                db.execute(query_insert, [name, class_, indexno, delivery_date, cost, all])
                db.commit()
                db.close()
                return render_template('templates/thank.html')

            except sqlite3.IntegrityError:
                db.close()
                return render_template('templates/order_too_many.html', type_ = '$2.50 meal')
            
        except sqlite3.IntegrityError:
            

            db.close()
            return render_template('templates/order_too_many.html', type_ = 'custom order')

#-----------------------------------------------------------------------------------------------
@app.route('/shopping_cart/')
def shopping_cart():
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')

    db = sqlite3.connect(file)

    query = '''
    SELECT * FROM Shopping_Cart
    '''

    cursor = db.execute(query)
    result = cursor.fetchall()

    total = 0.0
    for row in result:
        total += float(row[1]) * float(row[2])

    total = round(total, 2)

    db.close()
    from datetime import date
    date_time = date.today()
    #print(date_time) 

    date_time = str(date_time).split('-')
    #print(date_time) 
    day = int(date_time[2]) 
    month = int(date_time[1])
    year = int(date_time[0])
    if day < 29:
        day += 2
        actual = str(year) + '-' + str(month)+ '-' + str(day)

        print(actual)
        return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual,total = total)
    elif month != 12:
        month += 1
        day = 1
        actual = str(year) + '-' + str(month)+ '-' + str(day)
        print(actual)
        return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual, total = total)
    else:
        month = 1
        day = 1
        year += 1
        actual = str(year) + '-' + str(month)+ '-' + str(day)
        print(actual)
    return render_template('templates/order_cust_shoppingcart.html', result = result, total = total, date_ = actual)
    #return render_template('order_cust_shoppingcart.html', result = result, total = total)

#-----------------------------------------------------------------------------------------------
@app.route('/add_shopping_cart_c/')
def add_shopping_cart_c():
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')

    caiid = request.args['cai']
    print(caiid)

    db = sqlite3.connect(file)

    query_select = '''
    SELECT CaiFan_C.CaiName, CaiFan_C.CaiPrice FROM CaiFan_C WHERE CaiFan_C.CaiID = ?
    '''

    cursor = db.execute(query_select, [caiid])
    result = cursor.fetchone()
    result = list(result)
    name = result[0]
    price = result[1]
    print('name, price', name, price)
    

    
    try:
        query_insert = '''
        INSERT INTO Shopping_Cart(Name, Price, Quantity) VALUES(?,?,?)
        '''
        
        db.execute(query_insert, [name, price, 1])
        query_action = '''
        INSERT INTO Action_sc(Action, Attribute) VALUES(?, ?)
        '''
        db.execute(query_action, ['CREATE', name])
        db.commit()

    except sqlite3.IntegrityError:
        query_get_qty = '''
        SELECT Shopping_Cart.Quantity FROM Shopping_Cart WHERE Shopping_Cart.Name = ?
        '''
        query_action = '''
        INSERT INTO Action_sc(Action, Attribute) VALUES(?, ?)
        '''
        db.execute(query_action, ['UPDATE', name])
        cursor = db.execute(query_get_qty, [name])
        qty = cursor.fetchone()[0]
        print(qty)
        qty = int(qty) + 1
        query_update = '''
        UPDATE Shopping_Cart SET Quantity = ? WHERE Shopping_Cart.Name = ?
        '''

        db.execute(query_update, [qty, name])
        db.commit()

    query_get_all_c = '''
            SELECT * FROM CaiFan_C
    '''
    query_get_all_r = '''
            SELECT * FROM CaiFan_R
    '''

    cursor = db.execute(query_get_all_c)
    all_cai = cursor.fetchall()
    cursor = db.execute(query_get_all_r)
    all_rou = cursor.fetchall()

    db.close()

    
    
    return render_template('templates/order_cust_success.html', cai=all_cai, rou=all_rou)
#-----------------------------------------------------------------------------------------------
@app.route('/add_shopping_cart_r/')
def add_shopping_cart_r():
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')

    rouid = request.args['rou']
    print(rouid)

    db = sqlite3.connect(file)

    query_select = '''
    SELECT CaiFan_R.CaiName, CaiFan_R.CaiPrice FROM CaiFan_R WHERE CaiFan_R.CaiID = ?
    '''

    cursor = db.execute(query_select, [rouid])
    result = cursor.fetchone()
    result = list(result)
    name = result[0]
    price = result[1]
    print('name, price', name, price)
    

    
    try:
        query_insert = '''
        INSERT INTO Shopping_Cart(Name, Price, Quantity) VALUES(?,?,?)
        '''
        
        db.execute(query_insert, [name, price, 1])
        query_action = '''
        INSERT INTO Action_sc(Action, Attribute) VALUES(?, ?)
        '''
        db.execute(query_action, ['CREATE', name])
        
        db.commit()

    except sqlite3.IntegrityError:
        query_get_qty = '''
        SELECT Shopping_Cart.Quantity FROM Shopping_Cart WHERE Shopping_Cart.Name = ?
        '''
        query_action = '''
        INSERT INTO Action_sc(Action, Attribute) VALUES('UPDATE', ?)
        '''
        cursor = db.execute(query_get_qty, [name])
        db.execute(query_action, [name])
        db.commit()
        qty = cursor.fetchone()[0]
        print(qty)
        qty = int(qty) + 1
        query_update = '''
        UPDATE Shopping_Cart SET Quantity = ? WHERE Shopping_Cart.Name = ?
        '''

        db.execute(query_update, [qty, name])
        db.commit()

    query_get_all_c = '''
            SELECT * FROM CaiFan_C
    '''
    query_get_all_r = '''
            SELECT * FROM CaiFan_R
    '''

    cursor = db.execute(query_get_all_c)
    all_cai = cursor.fetchall()
    cursor = db.execute(query_get_all_r)
    all_rou = cursor.fetchall()

    db.close()

    
    
    return render_template('templates/order_cust_success.html', cai=all_cai, rou=all_rou)
#-----------------------------------------------------------------------------------------------
@app.route('/undo_shopping_cart/')
def undo_shopping_cart(): 

    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'library.db')
    db = sqlite3.connect(file)

    query_get_actions = '''
    SELECT * FROM Action_sc
    '''
    cursor = db.execute(query_get_actions)
    actions = cursor.fetchall()
    try:
        final_action  = actions[-1]
    except IndexError:
        query = '''
    SELECT * FROM Shopping_Cart
    '''

        cursor = db.execute(query)
        result = cursor.fetchall()

        total = 0.0
        for row in result:
            total += float(row[1]) * float(row[2])

        total = round(total, 2)

        db.close()
        from datetime import date
        date_time = date.today()
        print(date_time) 

        date_time = str(date_time).split('-')
        print(date_time) 
        day = int(date_time[2]) 
        month = int(date_time[1])
        year = int(date_time[0])
        if day < 29:
            day += 2
            actual = str(year) + '-' + str(month)+ '-' + str(day)

            print(actual)
            return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual,total = total)
        elif month != 12:
            month += 1
            day = 1
            actual = str(year) + '-' + str(month)+ '-' + str(day)
            print(actual)
            return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual, total = total)
        else:
            month = 1
            day = 1
            year += 1
            actual = str(year) + '-' + str(month)+ '-' + str(day)
            print(actual)
        return render_template('templates/order_cust_shoppingcart.html', result = result, total = total, date_ = actual)
        #return render_template('order_cust_shoppingcart.html', result = result, total = total)

    query_delete_final = '''
    DELETE FROM Action_sc WHERE Action_sc.ID = ?
    '''
    db.execute(query_delete_final, [final_action[0]])
    print(final_action)
    
    if final_action[1] == 'UPDATE':
        query_get_qty = '''
        SELECT Quantity FROM Shopping_Cart WHERE Name = ?
        '''
        
        cursor = db.execute(query_get_qty, [final_action[2]])
        qty = cursor.fetchone()[0]
        new_qty = int(qty) - 1

        query_update = '''
        UPDATE Shopping_Cart SET Quantity = ? WHERE Shopping_Cart.Name = ?
        '''
        db.execute(query_update, [new_qty, final_action[2]])
    else:
        query_delete_row = '''
        DELETE FROM Shopping_Cart WHERE Name = ?
        '''
        db.execute(query_delete_row, [final_action[2]])
    db.commit()
    query = '''
    SELECT * FROM Shopping_Cart
    '''

    cursor = db.execute(query)
    result = cursor.fetchall()

    total = 0.0
    for row in result:
        total += float(row[1]) * float(row[2])

    total = round(total, 2)

    db.close()
    from datetime import date
    date_time = date.today()
    print(date_time) 

    date_time = str(date_time).split('-')
    print(date_time) 
    day = int(date_time[2]) 
    month = int(date_time[1])
    year = int(date_time[0])

    if day < 29:
        day += 2
        actual = str(year) + '-' + str(month)+ '-' + str(day)

        print(actual)
        return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual,total = total)
    elif month != 12:
        month += 1
        day = 1
        actual = str(year) + '-' + str(month)+ '-' + str(day)
        print(actual)
        return render_template('templates/order_cust_shoppingcart.html', result = result, date_ = actual, total = total)
    else:
        month = 1
        day = 1
        year += 1
        actual = str(year) + '-' + str(month)+ '-' + str(day)
        print(actual)
    return render_template('templates/order_cust_shoppingcart.html', result = result, total = total, date_ = actual)



    


#-----------------------------------------------------------------------------------------------
@app.route('/gateway_order/')
def gateway_order():
    return render_template('templates/gateway_order.html')


#need improvement, only general ideas for now#-----------------------------------------------------------------------------------------------
@app.route('/hh')
def owner():
    return render_template('templates/owner.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)