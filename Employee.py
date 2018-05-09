#!/usr/bin/env python3

from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, Employee, User
from flask_httpauth import HTTPBasicAuth

# Anti Forgery State Token Code
from flask import session as login_session
import random
import string

# Import for 'Gconnect' step
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

auth = HTTPBasicAuth()

# refers to application_top
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))


CLIENT_ID = json.loads(open(APP_ROUTE + '/client_secrets.json',
                            'r').read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('postgresql://empcat:empcat@localhost/emp_catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
#  Define Program Constants
archival_flag_N = 'N'

# Create State token to prevent malicious request
# Store it in session for later validation


@app.route('/')
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        # print('APP_ROUTE' %APP_ROUTE )
        oauth_flow = flow_from_clientsecrets(APP_ROUTE + '/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code.decode('utf-8'))
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't then make new one.

    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        flash('Current user not logged in.')
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('employee_catalog'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected')
        return redirect(url_for('employee_catalog'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/department/<int:dept_id>/json')
def deprtmentdataJSON(dept_id):
    dept_data = session.query(Employee).filter_by(dept_id=dept_id).\
                filter_by(archival_flag=archival_flag_N).all()
    return jsonify(dept_emp_data=[i.serialize for i in dept_data])


@app.route('/')
@app.route('/home/')
def employee_catalog():
    all_dept = get_all_dept()
    emp_catalog = session.query(Employee).\
        filter_by(archival_flag=archival_flag_N).\
        order_by(Employee.start_date.desc()).limit(10)
    return render_template('employee_catalog.html',  emp_catalog=emp_catalog,
                           all_dept=all_dept)


@auth.login_required
@app.route('/<int:emp_id>/')
def get_emp_details(emp_id):
    if 'username' not in login_session:
        return redirect('/login')

    all_dept = get_all_dept()
    emp_details = session.query(Employee).filter_by(id=emp_id).\
        filter_by(archival_flag=archival_flag_N).one()
    for dept in all_dept:
        if dept.id == emp_details.dept_id:
            dept_name = dept.dept_name
    return render_template('empDetails.html', emp_details=emp_details,
                           all_dept=all_dept, dept_name=dept_name)


@app.route('/new/', methods=['GET', 'POST'])
def create_new_emp():
    if 'username' not in login_session:
        return redirect('/login')

    all_dept = get_all_dept()

    if request.method == 'POST':
        newemp = Employee(name=request.form['name'],
                          designation=request.form['designation'],
                          salary=request.form['salary'],
                          dept_id=get_dept_id(request.form['department']),
                          archival_flag='N',
                          desk_ph=request.form['desk_ph'],
                          emp_email=request.form['emp_email'],
                          city_state=request.form['city_state'],
                          reporting_manager=request.form['reporting_manager'],
                          user_id=login_session['user_id']
                          )
        session.add(newemp)
        session.commit()
        flash('New Employee %s Successfully Created' % newemp.name)
        return redirect(url_for('employee_catalog'))
    else:
        return render_template('newEmpRec.html', all_dept=all_dept)


@app.route('/edit/<int:emp_id>/', methods=['GET', 'POST'])
def edit_emp_rec(emp_id):
    if 'username' not in login_session:
        return redirect('/login')

    all_dept = get_all_dept()
    edt_rec = session.query(Employee).filter_by(id=emp_id).one()
    dept_name = get_dept(edt_rec.dept_id)
    if request.method == 'POST':
        if request.form['name']:
            edt_rec.name = request.form['name']
        if request.form['designation']:
            edt_rec.designation = request.form['designation']
        if request.form['salary']:
            edt_rec.salary = request.form['salary']
        if request.form['desk_ph']:
            edt_rec.desk_ph = request.form['desk_ph']
        if request.form['department']:
            edt_rec.dept_id = get_dept_id(request.form['department'])
        if request.form['emp_email']:
            edt_rec.emp_email = request.form['emp_email']
        if request.form['city_state']:
            edt_rec.city_state = request.form['city_state']
        if request.form['reporting_manager']:
            edt_rec.reporting_manager = request.form['reporting_manager']
        session.add(edt_rec)
        session.commit()
        flash('Employee %s Successfully Updated' % edt_rec.name)
        return redirect(url_for('employee_catalog', all_dept=all_dept))
    else:
        return render_template('editEmpRec.html', edt_rec=edt_rec,
                               dept_name=dept_name, all_dept=all_dept)


@app.route('/delete/<int:emp_id>', methods=['GET', 'POST'])
def del_emp_rec(emp_id):
    if 'username' not in login_session:
        return redirect('/login')

    arc_rec = session.query(Employee).filter_by(id=emp_id).one()
    if request.method == 'POST':
        arc_rec.archival_flag = 'Y'
        session.add(arc_rec)
        session.commit()
        return redirect(url_for('employee_catalog'))
    else:
        return render_template('delEmpRec.html', arc_rec=arc_rec)


@app.route('/department/<int:dept_id>')
def get_dept_data(dept_id):
    all_dept = get_all_dept()
    dept_data = session.query(Employee).filter_by(dept_id=dept_id).\
        filter_by(archival_flag=archival_flag_N).all()
    return render_template('employee_catalog.html',  emp_catalog=dept_data,
                           all_dept=all_dept)


def get_all_dept():
    all_dept = session.query(Department).all()
    return all_dept


def get_dept_id(dept_name):
    dept = session.query(Department).filter_by(dept_name=dept_name).one()
    return dept.id


def get_dept(dept_id):
    dept = session.query(Department).filter_by(id=dept_id).one()
    return dept.dept_name


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newuser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newuser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return (user.id)


if __name__ == '__main__':
    app.secret_key = 'super'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
