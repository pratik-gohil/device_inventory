from typing import Optional
from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.fields.html5 import DateField

from wtforms.validators import DataRequired, ValidationError, Optional
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

from os import environ


from flask_mail import Mail, Message

# Flask Instance
app = Flask(__name__, static_url_path='/static')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = environ.get('email')
app.config['MAIL_PASSWORD'] = environ.get('mail_pass')
app.config['MAIL_DEFAULT_SENDER'] = environ.get('email')

mail = Mail(app)

# Secret Key
app.config['SECRET_KEY'] = "secretknekvjnrkvjerkjn"

# Form
# Add Device Form
class DeviceForm(FlaskForm):
  name = StringField("Name :", validators=[DataRequired()])
  type = SelectField("Device Type :", choices=['Projector', 'Keyboard', 'Mouse', 'Monitor', 'Printer', 'CPU'], validators=[DataRequired()])
  company = StringField("Company :", validators=[DataRequired()])
  configuration = StringField("Configuration : (OPTIONAL)")
  os = StringField("Operating System : (OPTIONAL)")
  anti_virus_exp = DateField("Anti Virus Expiry Date : (OPTIONAL)", format="%Y-%m-%d", validators=[Optional()])
  submit = SubmitField("Submit")
  location = SelectField("Location :", choices=['Ground Floor Admin Table 1', 'Ground Floor Admin Table 2', "Ground Floor Principal Table 1","Ground Floor Account Table 1", "Ground Floor Account Table 2"])
  admin = SelectField("Admin :", choices=['Monika', 'Shweta'])

  def validate_name(self, name):
    device = Devices.query.filter_by(name = name.data).first()
    if device:
      raise ValidationError("Device Name Already Exists")

class ReportForm(FlaskForm):
  issue = StringField("Issue :", validators=[DataRequired()])
  message = TextAreaField('Message :', validators=[DataRequired()])


# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost/inventory"
# Initialize DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model
class Devices(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  type = db.Column(db.String(255), nullable=False)
  company = db.Column(db.String(255), nullable=False)
  configuration = db.Column(db.String(255))
  os_installed = db.Column(db.String(255))
  software_installed = db.Column(db.String(255))
  anti_virus_exp = db.Column(db.DateTime)
  location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
  admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

class Admin(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  dept = db.Column(db.String(255), nullable=False)
  office_contact = db.Column(db.String(255), nullable=False)
  office_contact_secondary = db.Column(db.String(255))
  personal_contact = db.Column(db.String(255), nullable=False)
  personal_contact_secondary = db.Column(db.String(255))
  email = db.Column(db.String(255), nullable=False, unique=True)

class Location(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(255), nullable=False, unique=True)

# Route decorator
@app.route('/')
def index():
  query = db.session.query(Devices, Location).join(Location).filter(Devices.location_id == Location.id).all()
  return render_template('index.html', query=query)

@app.route('/remove/<id>')
def remove(id):
  device = Devices.query.get_or_404(id)
  try:
    db.session.delete(device)
    db.session.commit()
    flash("Device Removed Successfully!!")
  except:
    flash('There was a problem removing device')
  finally:
    return redirect("/")

@app.route('/device/add', methods=['GET', 'POST'])
def device():
  form = DeviceForm()
  location = Location.query.filter_by(description=form.location.data).first()
  admin = Admin.query.filter_by(name=form.admin.data).first()
  if form.validate_on_submit():
    device = Devices(name=form.name.data, type=form.type.data, company=form.company.data, configuration=form.configuration.data, os_installed=form.os.data, anti_virus_exp=form.anti_virus_exp.data, location_id=location.id, admin_id=admin.id)
    db.session.add(device)
    db.session.commit()
    flash("Device Added Successfully")
  return render_template("new_device.html", form=form)

@app.route('/device/<id>', methods=['GET', 'POST'])
def info(id):
  form = ReportForm()
  query = db.session.query(Devices, Location, Admin).join(Location).join(Admin).filter(Devices.id == id)
  exp_date = None
  location = None
  admin = None
  for d, l, a in query:
    location = l
    admin = a
    try:
      exp_date = d.anti_virus_exp.date() - datetime.datetime.now().date()
      if exp_date.days < 1:
        exp_message = 'Expiry Date Is Due'
      else:
        exp_message = str(exp_date.days) + ' days left'
    except:
      exp_message = ""
    break

  if request.method == 'POST':
    try:
      msg = Message(form.issue.data, recipients=['sosav41477@geekale.com'])
      msg.html = """
      <div>
        <h1>{}</h1>
        <div>
          <h4>{}</h4>
        </div>
        <span>This is a computer generated email please don't reply</span>
      </div>
      """.format(form.message.data, location.description)
      mail.send(msg)
      flash("Your issue has been reported")
    except:
      flash("There was a problem")
  return render_template("device.html", id=id, query=query, form=form, exp_message=exp_message)

# serviceworker
@app.route('/serviceworker.js')
def sw():
  return app.send_static_file('serviceworker.js'), 200, {'Content-Type': 'text/javascript'}

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
  return render_template("500.html"), 500
