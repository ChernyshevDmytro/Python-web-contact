from datetime import datetime
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
from models import Person, Phones, Address, Files


UPLOAD_FOLDER = 'D:\\учеба\\goit-python\\Python_web\\team\\contacts\\uploads'
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx"}

engine = create_engine(
    "sqlite:///contacts.db", connect_args={"check_same_thread": False}
)
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


# contact contact details page
@app.route("/contacts", methods=["POST"], strict_slashes=False)
@app.route("/contact-details/", methods=["GET"], strict_slashes=False)
# find contact
def finding_contacts():
    if request.method == "POST":
        finding_name = request.form.get("find")
        finding_file_name = request.form.get("find_file")
        person_list = []
        files_list =[]
        for person in session.query(Person).all():
            if finding_name in person.name:
                person_list.append(person)
        
        for file in session.query(Files).all():
            if finding_file_name in file.file_name:
                files_list.append(file.file_name)
        
        if person_list:                      
            return render_template("contacts.html", persons=person_list)
        
        if files_list:                      
            return render_template("contacts.html", information_name=str(files_list))            
  
        if not person_list:            
            return render_template("contacts.html", information_name=f"Sorry no {finding_name} in persons name")   


        
        if files_list and person_list:                      
            return render_template("contacts.html", persons=person_list, information_name=files_list)



# contact index page
@app.route("/contacts", methods=["GET"], strict_slashes=False)
# all contacts showing
def showing_contacts():
    if request.method == "GET":
        persons = session.query(Person).all()
        if persons:
            return render_template("contacts.html", persons=persons, information_name=None)

# information about contact details
#@app.route("/contact-details/<id>", strict_slashes=False)
@app.route("/contact-information/<id>",methods=["GET"], strict_slashes=False)
def contacts(id):
    person = session.query(Person).filter(Person.id == id).first()
    #return render_template("contact-details.html", person=person)
    return render_template("contact-information_.html", person=person)


# contact adding
@app.route("/contact-information/", methods=["GET", "POST"], strict_slashes=False)
@app.route("/contact-information/<id>", methods=["GET", "POST"], strict_slashes=False)
# adding person and details
def add_person_and_details():
    excist = 0
    if request.method == "POST":
        person_name = request.form.get("name")
        person_birthday = request.form.get("birthday")
        person_phone = request.form.get("phones")
        person_email = request.form.get("email")
        person_country = request.form.get("country")
        person_city = request.form.get("city")
        person_street = request.form.get("street")
        person_building_number = request.form.get("building_number")
        person_flat_number = request.form.get("flat_number")

        for person in session.query(Person).all():

            if str(person_name) == str(person.name):
                excist = 1
                
                if person_birthday:
                    dt_birthday = datetime(
                        year=int(person_birthday[0:4]),
                        month=int(person_birthday[4:6]),
                        day=int(person_birthday[6:]),
                    ).date()
                    person.birthday = dt_birthday

                if person_phone and person.phones:
                    person.phones.append(Phones(phone=person_phone))
                if person_phone and not person.phones:
                    person.phones = [(Phones(phone=person_phone))]

                if person_email:
                    person.email = person_email

                if (
                    person_country
                    or person_city
                    or person_street
                    or person_building_number
                    or person_flat_number
                ):
                    current_address= session.query(Address).filter(Address.person_id==person.id).first()
                    if not current_address:
                        adddress = Address(
                            country=person_country,
                            city=person_city,
                            street=person_street,
                            building_number=person_building_number,
                            flat_number=person_flat_number,
                        )
                        person.address.append(adddress)
                        session.add(person)
                        session.commit()                    
                    else:
                        if person_country:
                            current_address.country=person_country
                        if person_city:
                            current_address.city=person_city                    
                        if person_street:
                            current_address.street=person_street                     
                        if person_building_number:
                            current_address.building_number=person_building_number
                        if person_flat_number:
                            current_address.flat_number=person_flat_number                     
                        session.add(current_address)
                        session.commit()

        if excist == 0:            
            person = Person(name=person_name)
            session.add(person)
            if  person_birthday:
                dt_birthday = datetime(
                    year=int(person_birthday[0:4]),
                    month=int(person_birthday[4:6]),
                    day=int(person_birthday[6:]),
                ).date()
                person.birthday = dt_birthday
                session.add(person)

            if  person_phone:
                person.phones.append(Phones(phone=person_phone))
                print(person_phone)
                session.add(person)
            
            if person_email:
                person.email = person_email

            if (
                person_country
                or person_city
                or person_street
                or person_building_number
                or person_flat_number
            ):
                adddress = Address(
                    country=person_country,
                    city=person_city,
                    street=person_street,
                    building_number=person_building_number,
                    flat_number=person_flat_number,
                )
                person.address.append(adddress)
            session.add(person)                       
            session.commit()

        return redirect("/contacts")   
    if request.method == "GET":
               
        return render_template("contact-information_.html", person=None)

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploads/<person_id>", methods=["GET", "POST"], strict_slashes=False)
# adding person and details
def upload_file(person_id):
    if request.method == 'POST' and int(person_id):         
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            person = session.query(Person).filter(Person.id == person_id).first()
            if person.data:
                person.data.append(Files(file_name=file.filename.rsplit('.', 1)[0].lower(), file_extension=file.filename.rsplit('.', 1)[1].lower(), file_storage_path=UPLOAD_FOLDER))
            if not person.data:
                    person.data = [(Files(file_name=file.filename.rsplit('.', 1)[0].lower(), file_extension=file.filename.rsplit('.', 1)[1].lower(), file_storage_path=UPLOAD_FOLDER))]            

            session.add(person)                       
            session.commit()           
            

            return redirect("/contacts")
    return '''
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''
@app.route('/download_file/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/contact-delete/<id>", strict_slashes=False)
def delete(id):
    session.query(Person).filter(Person.id == id).delete()
    session.commit()
    return redirect("/")


@app.route("/phone-delete/<id>", strict_slashes=False)
def delete_phone(id):
    session.query(Phones).filter(Phones.id == id).delete()
    session.commit()
    return redirect("/contacts")


@app.route("/phones/<id>", methods=["GET", "POST"], strict_slashes=False)
def edit_phone(id):

    if request.method == "POST":
        old_phone = session.query(Phones).filter(Phones.id == id).first()
        new_phone = request.form.get("new_phone")
        old_phone.phone = int(new_phone)
        session.add(old_phone)
        session.commit()
        print(new_phone)
        return redirect("/contacts")

    else:
        old_phone = session.query(Phones).filter(Phones.id == id).first()
        return render_template("phones.html", phone=old_phone.phone)


if __name__ == "__main__":
    app.secret_key = "super secret key"
    #app.config['SESSION_TYPE'] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.debug = True
    app.env = "development"
    app.run()
