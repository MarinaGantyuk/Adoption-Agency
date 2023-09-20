
from flask import Flask,render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional, AnyOf, URL, InputRequired
from flask_debugtoolbar import DebugToolbarExtension 
from models import db, connect_db, Pet
WTF_CSRF_SECRET_KEY='abc'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/adoption'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'abc'
connect_db(app)
#db.init_app(app)   
with app.app_context():
    db.create_all()

@app.route('/')
def pets_page():
    pets = db.session.execute(db.select(Pet)).scalars()
    return render_template('pet-list.html', pets = pets)

class Mypetform(FlaskForm):
    name=StringField('name', validators=[DataRequired()])
    species = SelectField(
        "Species",
        choices=[("cat", "Cat"), ("dog", "Dog"), ("porcupine", "Porcupine")],
    )
    photo_url=StringField('photo_url', validators=[Optional(), URL()])
    age=IntegerField('age', validators=[Optional(), NumberRange(min=0, max=30)])
    notes=TextAreaField('notes', validators=[Optional()])
    available=BooleanField('available', validators=[InputRequired()])
    submit=SubmitField('Add')
    
    def validate(self, extra_validators=None):
        resultvalidation=FlaskForm.validate(self)
        if not resultvalidation:
            return False
        return True


@app.route('/add', methods=['POST', 'GET'])
def addwt():
    form = Mypetform()

    if form.validate_on_submit():
        pet = Pet( 
            name = form['name'],
            species = form['species'],
            photo_url = form['photo_url'],
            age = form['age'],
            notes = form['notes'],
            available = bool(form['available'])
        ) 
        db.session.add(pet)
        db.session.commit()
        return redirect('/' + str(pet.id))
    
    return render_template('pet_wtform.html', form=form) 

@app.route('/<int:uid>', methods=['POST', 'GET'])
def editform(uid): 
    pet = Pet.query.get_or_404(uid) 
    form = Mypetform(obj=pet)

    if form.validate_on_submit():
        pet.name=form.name.data
        pet.notes = form.notes.data
        pet.available = form.available.data
        pet.photo_url = form.photo_url.data
        pet.species=form.species.data
        pet.veryfied = True 
        db.session.commit()
        return redirect('/')
    
    return render_template('pet-editform.html', form=form, uid=uid) 

@app.route('/add_all', methods=['POST', 'GET'])
def add_pet():
    if request.method == 'POST':
        pet = Pet( 
            name = request.form['name'],
            species = request.form['species'],
            photo_url = request.form['photo_url'],
            age = request.form['age'],
            notes = request.form['notes'],
            available = bool(request.form['available'])
        )
        db.session.add(pet)
        db.session.commit()
        return redirect('/pets/' + str(pet.id))

    return render_template('pet_addform.html')






