from flask import Flask, request, url_for, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'shhitsasecret'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(240))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))        
        
    def __init__(self, email, password):
        self.email = email
        self.password = password    

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')            


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            # TODO - "remember" that the user has logged in
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
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
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')  


@app.route("/blog")
def blog_page():
    posts = Blog.query.all()
    
    if request.method == 'GET': 
        if 'id' in request.args:
            post_id = request.args.get('id')
            content = Blog.query.get(post_id)
            return render_template('blog.html', content = content)

    return render_template('index.html', title="Blog Post",
              posts = posts)   

@app.route("/newpost")
def post():
    return render_template("newpost.html")

def is_blank(resp):
    if len(resp) == 0:
        return True
    else:
        return False     


@app.route("/newpost", methods=["POST"])
def new_post():
    title = request.form['title']
    body = request.form["body"]

    title_error = ""
    body_error = ""

    if is_blank(title):
        title_error = "Please fill in title"
        
    if is_blank(body):
        body_error = "Please fill in body"
        
    if not title_error and not body_error:
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        page_id = new_post.id
        return redirect("/blog?id={0}".format(page_id))

    else:
        return render_template("newpost.html",
            title = title,
            body = body,
            title_error = title_error,
            body_error = body_error
            )
                       
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')  


@app.route('/signup', methods=['POST'])
def signUp():
    _name = request.form['username']
    _email = request.form['email']
    _password = request.form['password']


if __name__ == "__main__":
    app.run()