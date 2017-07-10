import datetime
from flask import Flask, g
from flask import request, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import logout_user, login_required, login_user, current_user, LoginManager

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:supersecure@db/mb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecret'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
git
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.datetime.now()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Post(db.Model):
    id = db.Column('post_id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(50), nullable=False)
    content = db.Column('content', db.Text, nullable=False)
    pub_date = db.Column('pub_date', db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, title, content, pub_date=None):
        self.title = title
        self.content = content
        # self.user = user
        if pub_date is None:
            self.pub_date = datetime.datetime.now()


@app.before_first_request
def create_database():
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def show_all():
    return render_template('show_all.html', posts=Post.query.all())


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        if not request.form['content'] or not request.form['title']:
            flash('Please enter all the fields', 'error')
        else:
            title = request.form['title']
            content = request.form['content']
            post = Post(title, content)
            post.user = current_user
            db.session.add(post)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_all'))

    return render_template('add_post.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    user = User(request.form['username'], request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    registered_user = User.query.filter_by(username=username, password=password).first()
    if registered_user is None:
        flash('Username or password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')

    return redirect(url_for('show_all'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=80)
