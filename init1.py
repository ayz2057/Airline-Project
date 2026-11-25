#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='IntroDBPart2Pro',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')
@app.route('/search', methods=['GET'])
def search():
	source = request.args.get('source', '').strip()
	destination = request.args.get('destination', '').strip()
	departure_date = request.args.get('departure_date', '')
	trip_type = request.args.get('trip_type', 'one_way')
	return_date = request.args.get('return_date', '')
	cursor = conn.cursor()
	query = """
		SELECT f.*
		FROM Flight AS f
		JOIN Airport AS src ON f.dept_airport_name = src.name
		JOIN Airport AS dst ON f.arrival_airport_name = dst.name
		WHERE (src.city = %s OR src.name = %s)
		AND (dst.city = %s OR dst.name = %s)
		AND DATE(f.dept_datetime) = %s
		AND f.dept_datetime > NOW()
		ORDER BY f.dept_datetime
	"""
	cursor.execute(query, (
		source, source,
		destination, destination,
		departure_date
	))
	outbound_flights = cursor.fetchall()
	cursor.close()
	return render_template(
		'search_results.html',
		flights=outbound_flights
	)


#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')
@app.route('/login/customer')
def customer_login():
	return render_template('customer_login.html')

@app.route('/login/staff')
def staff_login():
	return render_template('staff_login.html')
#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')
@app.route('/register/customer')
def customer_register():
	return render_template('customer_register.html')
@app.route('/register/staff')
def staff_register():
	return render_template('staff_register.html')

#Authenticates the login
@app.route('/CustLoginAuth', methods=['GET', 'POST'])
def CustAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s and password = MD5(%s)'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['role'] = 'customer'
		session['username'] = email
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid password or email'
		return render_template('customer_login.html', error=error)
@app.route('/StaffLoginAuth', methods = ['POST'])
def StaffAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Airline_Staff WHERE username = %s and password = MD5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['role'] = 'staff'
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid password or email'
		return render_template('staff_login.html', error=error)
@app.route('/CustRegAuth', methods=['GET', 'POST'])
def CustRegAuth():
	#grabs information from the forms
	email = request.form['email']
	name = request.form['name']
	password = request.form['password']
	building_num = request.form['building_num']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_num = request.form['phone_num']
	passport_num = request.form['passport_num']
	passport_exp = request.form['passport_exp']
	passport_country = request.form['passport_country']
	dob = request.form['dob']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customer_register.html', error = error)
	else:
		ins = 'INSERT INTO Customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s,%s, %s, %s, %s)'
		cursor.execute(ins, (email, name, password, building_num, street, city, state, phone_num, passport_num, passport_exp, passport_country, dob))
		conn.commit()
		cursor.close()
		return render_template('index.html')
@app.route('/StaffRegAuth', methods=['POST'])
def StaffRegAuth():
    username = request.form['username']
    airline_name = request.form['airline_name']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    email = request.form['email']

    cursor = conn.cursor()
    query = 'SELECT * FROM Airline_Staff WHERE username = %s'
    cursor.execute(query, (username,))
    data = cursor.fetchone()

    if data:
        error = 'This username already exists'
        cursor.close()
        return render_template('staff_register.html', error=error)
    else:
        query = 'SELECT * FROM Airline WHERE name = %s'
        cursor.execute(query, (airline_name,))
        airline = cursor.fetchone()

        if not airline:
            cursor.close()
            error = 'This airline does not exist'
            return render_template('staff_register.html', error=error)

        ins = '''
            INSERT INTO Airline_Staff
            VALUES (%s, %s, MD5(%s), %s, %s, %s, %s)
        '''
        cursor.execute(ins, (
            username, airline_name, password,
            first_name, last_name, dob, email
        ))
        conn.commit()
        cursor.close()
        return render_template('index.html')
"""#Authenticates the register
@app.route('/RegisterAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')"""
@app.route('/home')
def home():
	if 'username' not in session:
		return redirect(url_for('login'))
	if session['role'] == 'customer':
		return render_template('customer_home.html', username = session['username'])
	elif session['role'] == 'staff':
		return render_template('staff_home.html', username = session['username'])
	else: return redirect(url_for('login'))
	"""username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)"""

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5001, debug = True)
