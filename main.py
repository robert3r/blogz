from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


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
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

return render_template('register.html')
@app.route('/blog', methods=['GET'])
def index():
    post_id = request.args.get("key_id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Build a Blog", blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        title_error = ''
        blog_error = ''
        title = request.form['title']
        blog = request.form['blog']
        if not title and not blog:  
            title_error = "please fill the title" 
            blog_error = "please fill the body"
            return render_template('newpost.html', title_error = title_error, blog_error=blog_error)
        elif not blog:  
                blog_error = "please fill the body" 
                return render_template('newpost.html', blog_error=blog_error, title_content=title) 
        elif not title:  
                title_error = "please fill the title" 
                return render_template('newpost.html', title_error = title_error, blog_content=blog)            
        else: 
            new_blog = Blog(title, blog)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?key_id=' + str(new_blog.id))
           
        
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()