from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner









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
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def main_blog():
    posts = Blog.query.all() 
    val = request.args.get('id')
    try:
        if val.isdigit() == True:
            entry = Blog.query.filter_by(id=val).first()
            return render_template('single_post.html', entry=entry)
    except:

        return render_template('blog.html', entries=posts)



#@app.route('/blog?id={{entry.id}}')
#def bpost_page():
    #info = Blog.query.filter_by(id='{{entry.id}}').first()
    #t = info.title
    #b = info.body
    
    #return render_template('register.html', entry=entry)   


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

    #    if request.method == 'POST':
#        task_name = request.form['task']
#        new_task = Task(task_name, owner)
#        db.session.add(new_task)
#        db.session.commit()

#    tasks = Task.query.filter_by(completed=False,owner=owner).all()
#    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
#    return render_template('todos.html',title="Get It Done!", 
#        tasks=tasks, completed_tasks=completed_tasks)




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        entry = Blog(title, body, owner) #************* owner id?????

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
        #entries = Blog.query.all()
        return render_template('newpost.html')








       #?????????????? user = User.query.filter_by(email=email).first()
        #if user and user.password == password:
        #    session['email'] = email
        #    flash("Logged in")
        #    return redirect('/')redirect
        #else:
         #   flash('User password incorrect, or user does not exist', 'error')

    


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
            flash('User does not exist', 'error') #Check to see if this works!

        else:
            flash('User password incorrect', 'error')


    return render_template('login.html')




@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        empty_string = ""

        def check_for_errors(username, password, verify):
        
            if username == "" or password == "" or verify == "":
                flash("One or more fields are invalid", 'error')

            if existing_user:
                flash("User already exists", 'error')
                
            if password != verify:
                flash("Password and password verify do not match", 'error')

            if len(username) < 3 and len(username) > 0:
                flash("Username is too short", 'error')

            if len(password) < 3 and len(password) > 0:
                flash("Password is too short", 'error')

        if check_for_errors(username, password, verify) and not existing_user and not empty_string:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Welcome,", '{{new_user}}')
            return redirect('/newpost')


    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


#@app.route('/', methods=['POST', 'GET'])
#def index():

#    owner = User.query.filter_by(email=session['email']).first()

#    if request.method == 'POST':
#        task_name = request.form['task']
#        new_task = Task(task_name, owner)
#        db.session.add(new_task)
#        db.session.commit()

#    tasks = Task.query.filter_by(completed=False,owner=owner).all()
#    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
#    return render_template('todos.html',title="Get It Done!", 
#        tasks=tasks, completed_tasks=completed_tasks)


#@app.route('/delete-task', methods=['POST'])
#def delete_task():

#    task_id = int(request.form['task-id'])
#    task = Task.query.get(task_id)
#    task.completed = True
#    db.session.add(task)
#    db.session.commit()

#    return redirect('/')


if __name__ == '__main__':
    app.run()