import os
import time
import qrcode
import hashlib
from flask import Flask, url_for, redirect, render_template, request, abort, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from wtforms import form, fields, validators
from flask.ext import admin, login, mail
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_security.forms import RegisterForm
from flask import make_response

from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib
from smtplib import SMTPException

import random
import string

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

cookies_users = db.Table('cookies_users',
                    db.Column('key', db.String()),
                    db.Column('value', db.String()))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class Cookie(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(80))      # unique=True
    value = db.Column(db.String(80))    # unique=True

    def __str__(self):
        return self.key + ' : ' + str(self.id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    has_scanned = db.Column(db.Boolean())
    forgotten_otp = db.Column(db.String(255))
    otp_auth = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

#class Cookies(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    value = db.Column(db.String(255))
#    key = db.Column(db.String(255))

class OneTimeLoginForm(form.Form):
    enterPasswd = fields.TextField(validators=[validators.required()])

    def generate_passwd(self, id):
        timeStamp = time.time()
        timeStamp = str(timeStamp)
        #print(timeStamp)
        timeStamp = timeStamp[:8]
        #print (timeStamp)
        #print(id)
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

    def validate_forgotten_otp(self, db_otp):
        if db_otp == self.enterPasswd.data:
            return True
        return False


class ForgottenPasswd(form.Form):
    email = fields.TextField('Email', validators=[validators.required()])


class ExtendedRegisterForm(RegisterForm):
    first_name = fields.TextField('First Name', validators=[validators.required()])
    last_name = fields.TextField('Last Name', validators=[validators.required()])

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


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
    return redirect(url_for('security.login', next=request.url, form=form))

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    print('############')
    print('admin route')
    print('############')
    form, user_data = get_form_user(request.form, current_user)
    #cookie = request.cookies.get(user_data)
    #print('############')
    #print(cookie)
    #print('############')
    if request.method == "POST" and form.validate():
        print("presiel submitom")
        print("##### user data id ", user_data.id)
        if form.validate_otp(str(user_data.id)) == True:
            user_data.has_scanned = True
            user_datastore.commit()
            print("prihlasil si sa, has_scanned sa zmenilo ", current_user.has_scanned)
            return render_template('index.html', form=form)
    else:
        print("nepresiel submitom")
    return render_template('admin/index.html', form=form,
                           admin_view=admin.index_view,
                           get_url=url_for,
                           h=admin_helpers)

@app.route('/newScan<id>', methods=[ 'GET','POST'])
def scan(id):
    print('############')
    print('new scan route')
    print('############')

    form, user_data = get_form_user(request.form, current_user)
    if request.method == "POST" and form.validate():
        print("presiel submitom")
        if form.validate_otp(id) == True:
            user_data.has_scanned = True
            user_datastore.commit()
            print("prihlasil si sa, has_scanned sa zmenilo ", current_user.has_scanned)
            return render_template('index.html', form=form)
        else:
            return render_template('admin/index.html', form=form,
                                   admin_view=admin.index_view,
                                   get_url=url_for,
                                   h=admin_helpers)
    else:
        print("nepresiel submitom")

    image = makeQr(login.current_user.id)
    print(os.path.dirname(os.path.realpath(__file__)))
    image.save(os.path.dirname(os.path.realpath(__file__)) + "/static/qr" + id + ".png", "PNG")
    return render_template('user.html', form=form)


@app.route('/scanned<id>',  methods=['GET', 'POST'])        #not used now
def scanned(id):
    print('############')
    print('already scanned')
    print('############')
    form, user_data = get_form_user(request.form, current_user)
    if request.method == "POST" and form.validate():
        print("presiel submitom")
        if form.validate_otp(id) == True:
            user_data.has_scanned = True
            user_datastore.commit()
            print("prihlasil si sa, has_scanned sa zmenilo ", current_user.has_scanned)
            return render_template('index.html', form=form)
    else:
        print("nepresiel submitom")
    return render_template('userScanned.html',
                           title='Sign In',
                           form=form)


@app.route('/makeCookie<id>', methods=['GET', 'POST'])
def makeCookie(id):
    print('############')
    print('makeCookie')
    print('############')
    form, user_data = get_form_user(request.form, current_user)
    if request.method == "POST" and form.validate():
        if form.validate_otp(id) == True:
            user_data.has_scanned = True
            user_data.otp_auth = True
            user_datastore.commit()
            cookie_key = Cookie(key=str(user_data.email))
            cookie_value = Cookie(value=user_data.last_name)
            db.session.add(cookie_key)
            db.session.add(cookie_value)
            db.session.commit()
            flash("OTP was correct, login was successful", 'success')
            #session['user_data.first_name'] = user_data.first_name
            resp = make_response(render_template('admin/index.html',
                                    admin_view=admin.index_view,
                                    get_url=url_for,
                                    h=admin_helpers,
                                    form=form))
            resp.set_cookie(str(user_data.email), user_data.last_name, httponly=False)
            return resp
    else:
        print("nepresiel submitom")
    return render_template('userScanned.html',
                           title='Sign In',
                           form=form)

@app.route('/resolveCookie<id>', methods=['GET', 'POST'])
def resolveCookie(id):
    print('############')
    print('resolveCookie')
    print('############')
    user_data = user_datastore.find_user(email=str(current_user))
    cookie = request.cookies.get(str(user_data.email))
    if cookie is None:
        abort(401)
    user_data.otp_auth = False
    user_datastore.commit()
    print('############')
    print(Cookie.query.filter_by(key=str(user_data.email)).first())
    print('############')
    #if cookie :
    #    abort(401)
    return render_template('index.html'), 200


@app.route('/newPassword', methods=['GET', 'POST'])
def newPassword():
    print('############')
    print('newPassword')
    print('############')
    form, user_data = get_form_user(request.form, form.email.data)
    if request.method == "POST":
        if user_data is None:
            print('############')
            print("wrong mail")
            print('############')
            flash('Password was not changed, we do not recognize given email.', 'error')
            #return redirect(url_for('security.login', next=request.url, form=form))
        else:
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
            user_data.password = encrypt_password(tmp_pass)
            user_datastore.commit()
            sendsmtp(form.email.data, tmp_pass)
            flash('Password successfully changed, check your email for new passwords.', 'success')
    return redirect(url_for('security.login', next=request.url, form=form))


@app.route('/newOtp<id>',  methods=['GET', 'POST'])
def newOtp(id):
    print('############')
    print('newOtp')
    print('############')
    form, user_data = get_form_user(request.form, current_user)
    if request.method == "POST" and form.validate():
        print('############')
        print("presiel submitom")
        print(user_data.forgotten_otp)
        print('############')

        if form.validate_forgotten_otp(user_data.forgotten_otp):
            user_data.forgotten_otp = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
            user_data.has_scanned = False
            user_datastore.commit()
            print("validate forgotten otp true")
            flash("Request approved, you can scan qr code again.", 'success')
            flash("Important, your new backup password is " + user_data.forgotten_otp, 'success')
            return render_template('admin/index.html',
                           admin_view=admin.index_view,
                           get_url=url_for,
                           h=admin_helpers,
                           form=form)
        else:
            flash("Your backup password wasn't correct, ask your admin about further steps.", 'error')
            print("wrong backup password")

    else:
        print("nepresiel submitom")
    if user_data.forgotten_otp is None:
        backup_otp = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
        user_data.forgotten_otp = backup_otp
        user_datastore.commit()
        flash("Your back-up password to allow scanning again is " + backup_otp + " \n It is advised to keep it in safe place, \n since it can be used only once.")

    return render_template('admin/index.html',
                           admin_view=admin.index_view,
                           get_url=url_for,
                           h=admin_helpers,
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
            last_name='Nimda',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role],
            has_scanned=False,
            forgotten_otp=None,
            otp_auth=False
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas'
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
                has_scanned=False,
                forgotten_otp=None,
                otp_auth=False
            )
        db.session.commit()
    return


def get_form_user(form, user_id):
    form = OneTimeLoginForm(request.form)
    user_data = user_datastore.find_user(email=str(user_id))
    return form,user_data


def sendsmtp(mail, new_passwd):
    msg = MIMEMultipart()
    email_text = "Dear user, your password was changed to " + new_passwd

    sender = 'juraj.maslej@gmail.com'
    recipient = mail
    passwd = 'xb7mj7ar'
    msg.attach(MIMEText(email_text))
    msg['From'] = 'juraj.maslej@gmail.com'
    msg['Subject'] = 'Request for new password'
    msg['To'] = mail
    try:
        server_ssl = smtplib.SMTP('smtp.gmail.com', 587)
        server_ssl.ehlo()
        server_ssl.starttls()
        server_ssl.login(sender, passwd)
    except SMTPException:
        print ("failed to login into the email")
        server_ssl.close()
    try:
        server_ssl.sendmail(sender, recipient, msg.as_string())
        server_ssl.close()
        print("successfully sent email to " + recipient)
    except:
        print("failed to sent email from " + sender + " to " + recipient)

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
    #build_sample_db()
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
