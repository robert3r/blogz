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

        username_error = ''
        password_error = ''
        user = User.query.filter_by(username=username).first()
        
        if username == "":
            username_error = 'That is not a valid username'
            username = ''
        if password == "":
            password_error = 'That is not a valid password'
            password = '' 
            username = username
        if not user:
            username_error = "Unregistered user, please go to signup first"   
        if user and user.password != password:    
            password_error = "Incorrect password, please remember it, not option yet for reset it"   
            username = username 
       
        if not username_error and not password_error: 
            session['user'] = user.username
            # TODO - "remember" that the user has logged in
            flash("Welcome "+ user.username)
            return redirect('/newpost')
        else:
            return render_template('login.html', title="Login", username = username, username_error = username_error, password_error = password_error)

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        
        existing_user = User.query.filter_by(username=username).first() 
        
        if len(username) < 3 or username == "":
            username_error = 'That is not a valid username'
            username = ''
        if len(password) < 3 or password == "":
            password_error = 'That is not a valid password'
            password = '' 
            username = username
        if verify != password:
            verify_error = 'Passwords do not match'
            username = username
            password = ''
            verify = ''
        if existing_user:
            username_error = "User already exist"
            username = ''
        
        if not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect('/newpost')
        else:
            return render_template('signup.html',title="Signup", username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)    
    
    return render_template('signup.html')

@app.route('/blog', methods=['GET'])
def blogs_list():
    post_id = request.args.get("key_id")
    user_id = request.args.get("user_id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Build a Blog", blog=blog)
    if user_id != None:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
        blogs = user.blogs
        return render_template('user_posts.html',title="User Blogs!", blogs=blogs)    
    
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs)

@app.route('/', methods=['GET'])
def index():
    post_id = request.args.get("key_id")
    user_id = request.args.get("user_id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Build a Blog", blog=blog)
    if user_id != None:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
        blogs = user.blogs
        return render_template('user_posts.html',title="User Blogs!", blogs=blogs)    
    
    users = User.query.all()
    return render_template('index.html',title="Blogs users!", 
        users=users)

@app.before_request
def require_login():
    allowed_routes = ['login','blogs_list','signup','index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
   
    allowed_routes = ['login','blog','signup','index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title_error = ''
        blog_error = ''
        title = request.form['title']
        blog = request.form['blog']
        #working on add the owner or username to the new blog
        owner = User.query.filter_by(username=session['user']).first()
        
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
            new_blog = Blog(title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?key_id=' + str(new_blog.id))
           
        
    return render_template('newpost.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()