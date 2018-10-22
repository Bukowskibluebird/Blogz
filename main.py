from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True) #should this be user or username?
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') #Change backref? (what is it?)

    def __init__(self, user, password):
        self.username = user
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def list_blogs():
    posts = Blog.query.all() 
    val = request.args.get('id')
    
    username = request.args.get('user')
    user_id = request.args.get('userID')
   
  
        
    try:

        if val:
            entry = Blog.query.filter_by(id=val).first()
            return render_template('single_post.html', entry=entry)

        elif user_id:
            entries = Blog.query.filter_by(owner_id=user_id).all()
            return render_template('single_author.html', entries=entries)


        else:
            if username.isalnum() == True:
                owner_id = username.owner_id
                
                entries = Blog.query.filter_by(owner_id=owner_id).all() 
                return render_template('single_author.html', entries=entries) #singlular or plural?

    except:

        return render_template('blog.html', entries=posts)



def blank_title(title):
    if title == "":
        return False
    else:
        return True

def blank_body(body):
    if body == "":
        return False
    else:
        return True





@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        entry = Blog(title, body, owner) 

        title_error = ''
        body_error = ''

        if not blank_title(title):
            title_error = "Need a title!"

        if not blank_body(body):
            body_error = "Need blog body!"

        if not title_error and not body_error:
            db.session.add(entry)
            db.session.commit()

            x = str(entry.id)

            return redirect('/blog?id=' + x)


        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error)


    else:
        return render_template('newpost.html')



@app.route('/')
def index():

    users = User.query.all() 
    user_id = request.args.get('userID')
    empty_string = ""

    #try:
        #if user_id.isdigit() == True:
            #user = Blog.query.filter_by(user=one_user).first() #necessary?
            #return redirect('/blog?userID={{user_id}}') #single or plural?
            #return render_template()
        
    #except:
    return render_template('index.html', users=users)

    


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        
        elif not user:
            flash('User does not exist', 'error') 

        else:
            flash('User password incorrect', 'error')


    return render_template('login.html')




@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(username=username).first()
        empty_string = ""

        
        
        if username == "" or password == "" or verify == "":
            flash("One or more fields are invalid", 'error')

        if existing_user:
            flash("User already exists", 'error')

        if len(username) < 3 and len(username) > 0:
            flash("Username is too short", 'error')

        if len(password) < 3 and len(password) > 0:
            flash("Password is too short", 'error')

        if password != verify:
            flash("Password and password verify do not match", 'error')



        if not existing_user:
            if username != empty_string or password != empty_string:
                if password == verify:
                    if len(username) > 2:
                        if len(password) > 2:
                            new_user = User(username, password)
                            db.session.add(new_user)
                            db.session.commit()
                            session['username'] = username
                            flash("Logged in")
                            return redirect('/newpost')


    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')



if __name__ == '__main__':
    app.run()