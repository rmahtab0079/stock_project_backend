from flask import Flask, jsonify, request, render_template_string
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin
from flask_cors import CORS


# app = Flask(__name__)
# app.config['MONGO_DBNAME'] = 'stocks'
# app.config['MONGO_URI'] = "mongodb://test2:test1234@ds137611.mlab.com:37611/stocks"
# mongo = PyMongo(app)

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': 'stock',
        'host': 'mongodb://test2:test1234@ds137611.mlab.com:37611/stocks?retryWrites=false'
    }

    # Flask-User settings
    USER_APP_NAME = "Flask-User MongoDB App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True   # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


# def create_app():
    """ Flask application factory """
    
    # Setup Flask and load app.config
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'stocks'
app.config['MONGO_URI'] = "mongodb://test2:test1234@ds137611.mlab.com:37611/stocks"
app.config.from_object(__name__+'.ConfigClass')
mongo = PyMongo(app)

    # Setup Flask-MongoEngine
db = MongoEngine(app)

# Define the User document.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Document, UserMixin):
    active = db.BooleanField(default=True)

    # User authentication information
    username = db.StringField(default='')
    password = db.StringField()

    # User information
    first_name = db.StringField(default='')
    last_name = db.StringField(default='')

    # Relationships
    roles = db.ListField(db.StringField(), default=[])

# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

# The Home page is accessible to anyone
@app.route('/', methods=['GET'])
def home_page():
    # String-based templates
    

    return render_template_string("""
        {% extends "flask_user_layout.html" %}
        {% block content %}
            <h2>Home page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)

@app.route('/register', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        req_data = request.get_json()
        username = req_data['username']
        password = req_data['password']
        print(username, password)
    return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data= "We received the request"), 200

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/members')
@login_required    # User must be authenticated
def member_page():
    # String-based templates
    return render_template_string("""
        {% extends "flask_user_layout.html" %}
        {% block content %}
            <h2>Members page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)

# return app

@app.route('/posts', methods=['GET'])
def PostList():
	posts = mongo.db.posts
	output = []
	for p in posts.find():
		output.append({'title': p['title'], 'content': p['content']})
	return jsonify({'result': output})

@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

    # Return the response in json format
    return jsonify(response)


@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('name')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Welcome {name} to our awesome platform!!",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no name found, please send a name."
        })

# @app.route('/')
# def index():
# 	return "<h1>Welcome to stock app server</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    # app = create_app()
    app.run(threaded=True, port=5000)