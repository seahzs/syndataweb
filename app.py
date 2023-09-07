from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SelectField, SubmitField
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
app.config['UPLOAD_FOLDER']='/uploads'

test_data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
            'Age': [28, 24, 35, 32],
            'City': ['New York', 'Paris', 'Berlin', 'London']}
data = pd.DataFrame(test_data)

class DataForm(FlaskForm):
    global data
    column_drop = SelectField(label='Drop Column', choices=data.columns.values)
    submit = SubmitField('Submit Now')

class UploadForm(FlaskForm):
    pass

@app.route("/")
@app.route("/home")
def homepage():
    return render_template('home.html', title='Home')

@app.route("/form", methods=['POST', 'GET'])
def formpage():
    global data
    if request.method == 'POST':
        to_drop=request.form['column_drop']
        data.drop(columns=[to_drop])
        return render_template('result.html', title='Result', result=f'Column "{to_drop}" has been dropped')
    else:
        form=DataForm()
        return render_template('form.html', title='Form', form=form)

@app.route("/upload", methods=['POST', 'GET'])
def uploadpage():
    global data
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(os.getcwd(),'uploads',filename)
        file.save(file_path)
        data = pd.read_csv(file_path)
        return render_template('result.html', title='Result', result=f'File "{filename}" has been uploaded')
    else:
        form=UploadForm()
        return render_template('upload.html', title='Upload', form=form)

@app.route("/table")
def tablepage():
    sample=data.head()
    return render_template('table.html', title='Table', tables=[sample.to_html(classes='data')], titles=sample.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
