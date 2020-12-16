from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, URL


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired(), Length(max=140)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LogoutForm(FlaskForm):
    """Empty form for passing CSRF token."""
    print("Logout!")

class UserEditForm(FlaskForm):
    """  Form for editing user info."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL',
                            validators=[Optional()])
    header_image_url = StringField('(Optional) Header Image URL',
                                   validators=[Optional()])
    bio = StringField('Bio', validators=[DataRequired(), Length(max=160)])
    location = StringField('Location', validators=[Optional(), Length(max=50)])
    password = PasswordField('Password', validators=[Length(min=6)])

class LikeForm(FlaskForm):
    """ for Like and unlike messages"""
