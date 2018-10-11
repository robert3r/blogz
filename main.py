from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/blog', methods=['GET'])
def index():
    post_id = request.args.get("id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Blog Submitted!", blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    title_error = ''
    blog_error = ''
    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        if title != '' and blog != '':
            new_blog = Blog(title, blog)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        else: 
            title_error = "please fill the title" 
            blog_error = "please fill the body"  
            return render_template('newpost.html', title_error = title_error, blog_error=blog_error)  
        
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()