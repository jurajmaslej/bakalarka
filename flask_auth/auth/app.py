import os
import time
import qrcode
import hashlib
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers


# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    has_scanned = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

class OneTimeLoginForm(form.Form):
    enterPasswd = fields.TextField(validators=[validators.required()])

    def generate_passwd(self, id):
        timeStamp = time.time()
        timeStamp = str(timeStamp)
        print(timeStamp)
        timeStamp = timeStamp[:8]
        print (timeStamp)
        print("ide sa hesovat " + timeStamp + " # " + id)
        passwd = hashlib.sha512((id + timeStamp).encode('utf-8')).hexdigest()
        print("heslo " + passwd[:8])
        return passwd

    def validate_otp(self, id):
        print("heslo vygenerovane serverom ", self.generate_passwd(id)[:8])
        print("heslo natukane do formu ", self.enterPasswd.data)
        if self.generate_passwd(id)[:8] == self.enterPasswd.data:
            print("hesla sa zhoduju ")
            return True
        return False

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url, form=form), form=form)

# Flask views
@app.route('/')
def index():
    print('############')
    print('index route')
    print('############')
    form = OneTimeLoginForm(request.form)
    return render_template('index.html', form=form)

@app.route('/admin/')
def admin():
    print('############')
    print('admin route')
    print('############')
    form = OneTimeLoginForm(request.form)
    return render_template('admin/index.html', form=form,
                           admin_view=admin.index_view,
                           get_url=url_for,
                           h=admin_helpers)

@app.route('/newScan<id>')
def scan(id):
    print("ahoj")
    image = makeQr(login.current_user.id)
    print(os.path.dirname(os.path.realpath(__file__)))
    image.save(os.path.dirname(os.path.realpath(__file__)) + "/static/qr" + id + ".png", "PNG")
    return render_template('user.html', form=form)


@app.route('/scanned<id>',  methods=['GET', 'POST'])
def scanned(id):
    print("ahojj, ", current_user.has_scanned)
    form = OneTimeLoginForm(request.form)
    #print(time.time())
    #print(current_user)
    user_data = user_datastore.find_user(email=str(current_user))
    if request.method == "POST" and form.validate():
        print("presiel submitom")
        if form.validate_otp(id) == True:
            user_data.has_scanned = True
            user_datastore.commit()
            print("prihlasil si sa, has_scanned sa zmenilo " , current_user.has_scanned)
            return render_template('index.html', form=form)
    else:
        print("nepresiel submitom")
    return render_template('userScanned.html',
                           title='Sign In',
                           form=form)

# Create admin
admin = flask_admin.Admin(
    app,
    'Example: Auth',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(User, db.session))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
        form=form
    )


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role],
            has_scanned=False
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=encrypt_password(tmp_pass),
                roles=[user_role, ],
                has_scanned=False
            )
        db.session.commit()
    return


def makeQr(user_id):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        time1 = time.time()
        time1 = round(time1)
        time1 = int(time1)
        time1 = str(time1)
        time1 = time1[:10] ##sekundova presnost
        print("cas co ide do qr kodu " + time1)
        qr.add_data( time1 + "#" +str(user_id))
        qr.make(fit=True)

        return qr.make_image()


def serve_pil_image(pil_img):

    img_io = StringIO()
    pil_img.save(img_io, 'PNG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
