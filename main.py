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