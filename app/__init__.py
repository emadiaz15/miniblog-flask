from flask import Flask, g, redirect, url_for,render_template,request,session,flash,abort
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = '123456'
global db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models.usuarios import User
from app.models.categorias import Category
from app.models.posteos import Post

@app.context_processor
def listCategories():
    categories = Category.query.all()
    return dict(categories = categories)
    
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        error = None

        # Validación de campos requeridos
        if User.query.filter_by(username=username).first() is not None:
            error = 'User {} is already registered.'.format(username)
        elif not password == password_confirm:
            error = 'The passwords entered do not match.'
        if User.query.filter_by(email=email).first() is not None:
            error = 'Email {} is already registered.'.format(email)

        if error is None:
            # Crear una instancia del modelo User
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                email=email,
                created_at=datetime.now(),
            )
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

        flash(error)
    
    if not g.user is None:
        return redirect(url_for('home'))

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password, password):
            error = 'Usuario/Contraseña invalido'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('home'))
        
        flash(error)

    if not g.user is None:
        return redirect(url_for('home'))

    return render_template('auth/login.html')

@app.route('/home',methods=['GET', 'POST'])
@login_required
def home():
    return render_template('blog/home.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/categorias/<int:id>')
def show_category(id:int):
    show_select = Category.query.filter_by(id=id).first()
    if show_select is None:
        abort(404)
    posts = Post.query.filter_by(category_id=show_select.id)
    posts = list(posts)
    authors = list()
    for post in posts:
        user = User.query.get(post.author_id)
        authors.append(user.username)
            
    return render_template('blog/category.html',show_category=show_select,posts=posts,authors=authors)

@app.route('/create_post',methods=['POST'])
def create_post():
    title = request.form['title']
    content = request.form['content']
    category_id = int(request.form['category_id'])
    
    new_post = Post(
                title = title,
                content = content,
                author_id = g.user.id,
                category_id = category_id,
            )
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(url_for('show_category',id=category_id))