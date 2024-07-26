import secrets
import os
from PIL import Image
from flask import  render_template, redirect, url_for, flash, request, abort

from flaskblog import app, db, bcrypt

from flaskblog.forms import LoginForm, RegistrationForm, UpdateAccountForm, PostForm

from flaskblog.models import User, Post

from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_


# posts = [
#     {
#         'name': 'Solomon Adule',
#         'content': 'First post',
#         'date_posted': 'December 28th, 2023'
#     },
#     {
#         'name': 'Gladys Omereji',
#         'content': 'Second post',
#         'date_posted': 'December 29th, 2023'
#     }
    
# ]


@app.route('/', methods=['GET', 'POST'])
def index():
    
    posts = Post.query.all()
    return render_template('index.html', posts=posts, title='Home')

@app.route('/about', methods=['GET', 'POST'])
def about():
    posts = Post.query.all()
    return render_template('index.html', posts=posts, title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    if form.validate_on_submit():
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        
        try:
            new_user = User(username=form.username.data,email=form.email.data, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
        except:
            return 'failed to create new user'
        
        flash("Account created for {}".format(form.username.data))
        print(form.username.data) 
           
        return redirect(url_for('account'))
    else:
        print(form.errors)
        
    return render_template('register.html', title='Register', form = form)
    

@app.route('/login/', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        
        try:
            user = User.query.filter( User.email == form.email.data).first()
            
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                
                login_user(user, remember=form.remember.data)
                flash(f'login successful')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            
            else:
            
                flash('Please check email and password!')
                
                return redirect(url_for('login'))
        except Exception as e:
            print(f'Error: {str(e)}')
            
            
        
    return render_template('login.html', title='Login', form=form)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pix', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path)
    
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            
            current_user.image_file = picture_file
            print(f'picture filename is: {picture_file}')
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully')
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    image_file = url_for('static', filename='profile_pix/' + current_user.image_file)
    print(current_user.image_file)
    print(form.errors)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        
        flash('Your post has been created!')
        return redirect(url_for('index'))
    
    return render_template('create_post.html', title='New Post', form=form, legend='Post')

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        # abort(403)
        return redirect(url_for('index'))
        
    form = PostForm()
    
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        
        flash('Post Updated Successfully!')
        return redirect(url_for('index'))
    
    elif request.method == "GET":
        
        form.title.data = post.title
        form.content.data = post.content
        
    return render_template('create_post.html', title='Update post', form=form, legend='Update')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    
    post = Post.query.get_or_404(post_id)
    
    if post.author == current_user:
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted!")
        
        return redirect(url_for('index'))
    else:
        flash("Sorry Cannot Delete Post")
        # abort(403)
        return redirect(url_for('index'))
        
    