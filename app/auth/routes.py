from app import db
from app.auth import bp
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user,login_required,logout_user
from app.models import User
from werkzeug.urls import url_parse
from app.auth.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from app.api.errors import bad_request
from app.auth.email import send_password_reset_email, send_sign_up_req_email, send_req_result_email

# Signup
#----------------------------------------------------------
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('admin.createsession'))
    form = SignupForm()
    if form.validate_on_submit():
        # Superadmin account is approved upon signup
        if form.email.data.lower() == "emotionappmoodtrack@gmail.com":
            user = User(first_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data, orcid=form.orcid.data, institution=form.institution.data, \
            email=form.email.data.lower(), reason=form.reason.data, approved=True)
        else:
            user = User(first_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data, orcid=form.orcid.data, institution=form.institution.data, \
            email=form.email.data.lower(), reason=form.reason.data, approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        #email superadmin about new sign up request
        send_sign_up_req_email(user)
        
        flash('Congratulations, your signup has been requested!')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', title='Sign up', form=form, is_signup=True, test ='pass')


# Login/Sign In
#----------------------------------------------------------
@bp.route('/')
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.createsession'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # Flash error message if credentials are incorrect
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password, please check your email and password.')
            return redirect(url_for('auth.login'))
        # Flash error message if account is not yet approved
        elif user.approved == False:
             flash('Your sign up request is pending approval.')
             return render_template('auth/login.html', title='Login', form=form, is_signin=True)
        
        # Log user in if credentials are correct and redirect them to the desired page if specified
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.createsession')
        return redirect(next_page)

    return render_template('auth/login.html', title='Login', form=form, is_signin=True)


# Logout
#----------------------------------------------------------
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Reset Password
#----------------------------------------------------------
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password. If you couldn't find the email in your inbox, please check your spam/junk folder ")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.createsession'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

