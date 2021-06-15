from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, RadioField
from wtforms.validators import InputRequired, EqualTo, Length

class RegisterForm(FlaskForm):
    user_id = StringField("", render_kw={"placeholder": "User ID"}, validators=[InputRequired()])
    password = PasswordField("", render_kw={"placeholder": "Password"},validators=[InputRequired()])
    password2 = PasswordField("", render_kw={"placeholder": "Confirm Password"},validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user_id = StringField("", render_kw={"placeholder": "User ID"}, validators=[InputRequired()])
    password = PasswordField("", render_kw={"placeholder": "Password"},validators=[InputRequired()])
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    search = StringField("", render_kw={"placeholder": "Artist"},validators=[InputRequired()])
    submit = SubmitField("Search")

class AddStockForm(FlaskForm):
    title = StringField("", render_kw={"placeholder": "Title"},validators=[InputRequired()])
    artist = StringField("", render_kw={"placeholder": "Artist"}, validators=[InputRequired()])
    length = StringField("", render_kw={"placeholder": "Length"}, validators=[InputRequired()])
    price = StringField("", render_kw={"placeholder": "Price"},validators=[InputRequired()])
    stock = IntegerField("", render_kw={"placeholder": "Stock"}, validators=[InputRequired()])
    stockFormat = SelectField("Format:",choices = [("vinyl","Vinyl"),("CD","CD")], validators=[InputRequired()])
    submit = SubmitField("Add Stock")

class RemoveStockForm(FlaskForm):
    record_id = StringField("", render_kw={"placeholder": "Record ID"}, validators=[InputRequired()])
    submit = SubmitField("Remove")

class EditStockForm(FlaskForm):
    record_id = StringField("", render_kw={"placeholder": "Record ID"}, validators=[InputRequired()])
    length = StringField("", render_kw={"placeholder": "Length"}, validators=[InputRequired()])
    price = StringField("", render_kw={"placeholder": "Price"},validators=[InputRequired()])
    stock = IntegerField("", render_kw={"placeholder": "Stock"},validators=[InputRequired()])
    submit = SubmitField("Edit Stock")

class ReviewForm(FlaskForm):
    review = StringField("", render_kw={"placeholder": "Leave a review"},validators=[InputRequired(),Length(max=100)])
    stars = SelectField("", render_kw={"placeholder": "Leave a review"}, choices = [("*","*"),("**","**"),("***","***"),("****","****"),("*****","*****")], validators=[InputRequired()])
    submit = SubmitField("Submit")

class AddUserForm(FlaskForm):
    user_id = StringField("", render_kw={"placeholder": "User ID"},validators=[InputRequired()])
    password = PasswordField("", render_kw={"placeholder": "Password"}, validators=[InputRequired()])
    password2 = PasswordField("", render_kw={"placeholder": "Confirm Password"},validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Add User")