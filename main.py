from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Yes@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username=username
        self.password=password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    user_id = db.Column(db.String(50), db.ForeignKey('user.username'))

    def __init__(self, name, body, user):
        self.name=name
        self.body=body
        self.user=user

@app.before_request
def require_login():
    allowed_routes = ['index', 'blogs', 'register', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You need to be logged in to access this")
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ''
        password_error = ''

        #username errors#
        if username == '':
            username_error = "Username error"
        if len(username) > 20:
            username_error = "Username error"
        else:
            if len(username) < 3:
                username_error = "Username error"
        if ' ' in username:
            username_error = "Username error"

        #password errors#
        if password == '':
            password_error = "Password error"
        if len(password) > 20:
            password_error = "Password error"
        else:
            if len(password) < 3:
                password_error = "Password error"
        if ' ' in password:
            password_error = "Password error"

        if not password_error and not username_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return "<h1>Duplicate user</h1>"
        else:
            return render_template('signup.html', 
            password_error=password_error, 
            username_error=username_error)
            
    return render_template('signup.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()

    if request.method == 'GET':
        if 'blogs' in request.args:
            user = request.args.get('blogs')
            posts = Blog.query.filter_by(user_id=user).all()
            return render_template("blogs.html", posts=posts)

    return render_template('index.html', title = "Nik's Blog", users=users)

@app.route("/blogs")
def blogs():
    posts = Blog.query.all()

    if request.method == 'GET':
        if 'id' in request.args:
            post_id = request.args.get('id')
            content = Blog.query.get(post_id)
            return render_template("post.html", content=content)
        if 'user' in request.args:
            user_id = request.args.get('user')
            posts = Blog.query.filter_by(user_id=user_id).all()
            return render_template("blogs.html", posts=posts)

    encoded_error = request.args.get("error")
    return render_template('blogs.html', title = "Nik's Blog", posts=posts, error=encoded_error and cgi.escape(encoded_error, quote=True))

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out")
    return redirect('/blogs')

@app.route("/add", methods=["POST"])
def add_blog():
    blog_name = request.form['name']
    blog_body = request.form['body']
    user      = User.query.filter_by(username=session['username']).first()

    if blog_name == "":
        error = "Cannot leave blank."
        return render_template("newpost.html", error=error)

    if blog_body == "":
        error = "Cannot leave blank."
        return render_template("newpost.html", error=error)

    blog = Blog(blog_name, blog_body, user)
    db.session.add(blog)
    db.session.commit()
    post_id = blog.id
    content=Blog.query.get(post_id)

    return render_template("post.html", content=content)

@app.route("/newpost", methods=['GET'])
def newpost():
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()