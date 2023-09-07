from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from secrets import token_urlsafe
import os
from fileinput import filename
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
key = token_urlsafe(16)
app.secret_key = key
csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER']='uploads'

data = {
    'Name': ['John', 'Anna', 'Peter', 'Linda'],
    'Age': [28, 24, 35, 32],
    'City': ['New York', 'Paris', 'Berlin', 'London']
}

df = pd.DataFrame(data)

class DataForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email Add', validators=[DataRequired()])
    submit = SubmitField('Submit Now')

class UploadForm(FlaskForm):
    pass

@app.route("/")
@app.route("/home")
def homepage():
    return render_template('home.html', title='Home')

@app.route("/form", methods=['POST', 'GET'])
def formpage():
    if request.method == 'POST':
        return render_template('result.html', title='Result', result=request.form['name'])
    else:
        form=DataForm()
        result=''
        if form.validate_on_submit():
            result=form.name.data
            flash(form.name.data)
            return redirect(url_for('home'))
        return render_template('form.html', title='Form', form=form)

@app.route("/upload", methods=['POST', 'GET'])
def uploadpage():
    if request.method == 'POST':
        f = request.files.get('file')
        data_filename = secure_filename(f.filename)
        data_file_path = os.path.join(app.config['UPLOAD_FOLDER'],data_filename)
        f.save(data_file_path)
        data = pd.read_csv(data_file_path, encoding='unicode_escape')
        return render_template('result.html', title='Result', result=f'File {data_filename} has been uploaded')
    else:
        form=UploadForm()
        return render_template('upload.html', title='Upload', form=form)

@app.route("/table")
def tablepage():
    return render_template('table.html', title='Table', tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
