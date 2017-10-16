from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Yes@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, name, body):
        self.name = name
        self.body = body

@app.route("/")
def index():
    posts = Blog.query.all()
    
    if request.method == 'GET':
        if 'id' in request.args:
            post_id = request.args.get('id')
            content = Blog.query.get(post_id)
            return render_template("post.html", content=content)

    encoded_error = request.args.get("error")
    return render_template('blogs.html', title = "Nik's Blog", posts=posts, error=encoded_error and cgi.escape(encoded_error, quote=True))

@app.route("/add", methods=["POST"])
def add_blog():
    blog_name = request.form['name']
    blog_body = request.form['body']

    if blog_name == "":
        error = "Cannot leave blank."
        return render_template("newpost.html", error=error)

    if blog_body == "":
        error = "Cannot leave blank."
        return render_template("newpost.html", error=error)

    blog = Blog(blog_name, blog_body)
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