from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from flask_restful import Api, Resource

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api = Api(app)

# бд
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# логин менеджер
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default.png')

# загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# главный экран
@app.route("/")
def krasivoview():
    return render_template("krasivoview.html")

# секрет
@app.route("/MikleJordan")
@login_required
def MikleJordan():
    return render_template("EgoVosdyshestvo.html")

# регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # проверка
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Ты уже существует"

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# логин
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("profile"))
        else:
            return "Но но но видимо у тебя неверный логин или пароль или ты не зарегестрейшенился"

    return render_template("login.html")

# профиль
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# изменение аватара
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            current_user.avatar = filename
            db.session.commit()

            return redirect(url_for("profile"))

    return render_template("upload.html")

# список людей зарегестривовшихся на сайте
class UserAPI(Resource):
    def get(self):
        users = User.query.all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar
            }
            for user in users
        ]

api.add_resource(UserAPI, "/api/users")

# выход
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("krasivoview"))


if __name__ == "__main__":
    app.run(debug=True)

# pip freeze > requirements.txt