# Code Citations

## License: unknown
https://github.com/Faruq-06/CCLab1/tree/0a4632819219231fe66c0c1226ebec6dfdd0f33d/Validation.py

```
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request
```


## License: unknown
https://github.com/DanieIIa/SQLInjection/tree/78c667c9a3ba1901d94e593371387f2552285402/phytonlogin/index.py

```
('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password
```


## License: unknown
https://github.com/Emmeix/ExpenseTracker/tree/ebbe8e4a09210bd92054cc472266803bd3e27bc1/webapp.py

```
username, password))
    account = cursor.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return redirect(url_for('
```


## License: unknown
https://github.com/golu244566/myfirstweb/tree/7383d3bae7acfc1248d540fe12336d93c15d9c2a/app.py

```
= %s AND password = %s', (username, password))
    account = cursor.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account
```


## License: unknown
https://github.com/Papillor/authentication_rolebased_flask_psql/tree/7f8d4fc0a5b6fff09c29ccd69eb4152ac150b666/app/routes/auth.py

```
execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account['id'
```

