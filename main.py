from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content')
    submit = SubmitField("Submit Post")


# Read the database and post all blog entered
@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


# Pull the blog post specified
@app.route("/post/<int:index>", methods=["GET"])
def show_post(index):
    search_post = BlogPost.query.get(index)
    return render_template("post.html", post=search_post)


# New blog entry screen
@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    post_form = CreatePostForm()
    if post_form.validate_on_submit():
        x = datetime.now()
        db_date = x.strftime("%B %d,%Y")
        new_blog_post = BlogPost(
            title=post_form.title.data,
            subtitle=post_form.subtitle.data,
            author=post_form.author.data,
            img_url=post_form.img_url.data,
            body=post_form.body.data,
            date=db_date,
        )
        print(new_blog_post)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=post_form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    post_form = CreatePostForm()
    if request.method == 'GET':
        post_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            author=post.author,
            img_url=post.img_url,
            body=post.body
        )
    elif request.method == 'POST':
        if post_form.validate_on_submit():
            post.title = post_form.title.data
            post.subtitle = post_form.subtitle.data
            post.author = post_form.author.data
            post.img_url = post_form.img_url.data
            post.body = post_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", index=post_id))
    return render_template("make-post.html", form=post_form, is_edit=True)


@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete(index):
    post_to_delete = BlogPost.query.get(index)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)