from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import time, datetime

app = Flask(__name__)
app.secret_key = "asdfghjkl"

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///covid_center_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the Vaccination Center model
class Vaccination_Center(db.Model):
    __tablename__ = 'vaccination_center'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slots_per_day = db.Column(db.Integer, nullable=False, default=10)
     # Relationship to slot_detail
    slots_booked = db.relationship('SlotDetail', backref='center', lazy=True)

    def working_hours(self):
        return datetime.combine(datetime.min, self.end_time) - datetime.combine(datetime.min, self.start_time)

# Define the User model using UserMixin for user management
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Relationship to slot_detail
    booked_slots = db.relationship('SlotDetail', backref='user', lazy=True)

# Define slot_detail model
class SlotDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booked_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    center_id = db.Column(db.Integer, db.ForeignKey('vaccination_center.id'), nullable=False)
    booked_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        if current_user.is_admin :
            return redirect(url_for('admin_dashboard'))
        # Fetch all vaccination centers if user is authenticated
        vaccination_centers = Vaccination_Center.query.all()
        return render_template('index.html', vaccination_centers=vaccination_centers, current_user=current_user)
    else:
        return redirect(url_for('login'))
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, is_admin=False).first()

        if user and check_password_hash(user.password, password):
            # Login user if credentials are correct
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    # Render the login form if it's a GET request or login failed
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password1']
        confirm_password = request.form['password2']
        is_admin = False  # Ensure default value for non-admin users

        if password != confirm_password:
            return "Password DO Not Match"

        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password, is_admin=is_admin)  # Ensure is_admin is set correctly
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html')



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin_user = User.query.filter_by(email=email, is_admin=True).first()

        if admin_user:
            if check_password_hash(admin_user.password, password):
                # Login admin user if credentials are correct
                login_user(admin_user)
                return redirect(url_for('admin_dashboard'))
            else:
                return "Invalid credentials"
        else:
            # Create a new admin user if not found
            hashed_password = generate_password_hash(password)
            new_admin = User(name="", email=email, password=hashed_password, is_admin=True)  # Ensure is_admin is set to True for admin users
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin)
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')



@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.is_admin:
        if request.method == 'POST':
            name = request.form['CenterName']
            address = request.form['CenterAddress']
            start_time_str = request.form['StartTime']
            end_time_str = request.form['EndTime']

            # Convert strings into original timings
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            # Create a new Vaccination Center entry
            new_center = Vaccination_Center(name=name, address=address, start_time=start_time, end_time=end_time)
            db.session.add(new_center)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            # Fetch all centers data for rendering dashboard
            centers_data = Vaccination_Center.query.all()
            return render_template('admin_dashboard.html', admin=current_user, centers=centers_data)
        


@app.route('/book_slot/<int:id>',  methods = ['GET','POST'])
@login_required
def book_slot(id):
    if current_user.is_authenticated and not current_user.is_admin:
        if request.method == 'POST':
           center = Vaccination_Center.query.filter_by(id=id).first()
           if center.slots_per_day > 0 : # Check if there are available slots
               date_str = request.form['Date']
               time_str = request.form['Time']

               # Convert the date and time strings to a datetime object
               booked_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
               # Check if booked time is within working hours
               if center.start_time <= booked_datetime.time() <= center.end_time:
                    new_booked_slot = SlotDetail(user_id=current_user.id, center_id=center.id, booked_date=booked_datetime.date(), booked_time=booked_datetime)
                    db.session.add(new_booked_slot)
                    center.slots_per_day -= 1  # Decrement the available slots
                    db.session.commit()
                    return redirect(url_for('home'))
               else:
                   return 'Invalid Slot Time'
           else:
               return "No slots available for this center"
        
        vaccination_center_data = Vaccination_Center.query.filter_by(id=id).first()
        return render_template('book_slot.html', center_data = vaccination_center_data, current_user = current_user)



@app.route('/booking_details', methods=['GET', 'POST'])
@login_required
def booking_details():
    if current_user.is_authenticated and not current_user.is_admin:
        booked_slots = SlotDetail.query.filter_by(user_id=current_user.id).all()
        return render_template('booking_details.html', booked_slots=booked_slots, current_user=current_user)
    
    return redirect(url_for('home'))



@app.route('/edit_center/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_center(id):
    if current_user.is_admin:
        if request.method == 'POST':
            new_name = request.form['NewCenterName']
            new_address = request.form['NewCenterAddress']
            new_start_time_str = request.form['NewStartTime']
            new_end_time_str = request.form['NewEndTime']

            # Convert strings into original timings
            start_time = datetime.strptime(new_start_time_str, '%H:%M').time()
            end_time = datetime.strptime(new_end_time_str, '%H:%M').time()

            # Update details for the specified center
            update_center_data = Vaccination_Center.query.filter_by(id=id).first()
            update_center_data.name = new_name
            update_center_data.address = new_address
            update_center_data.start_time = start_time
            update_center_data.end_time = end_time
            db.session.commit()
            return redirect(url_for('admin_dashboard'))

        # Fetch center data for editing
        update_center_data = Vaccination_Center.query.filter_by(id=id).first()
        return render_template('edit_center.html', center_data=update_center_data, admin=current_user)



@app.route('/delete_center/<int:id>', methods=['GET', 'POST'])
def delete_center(id):
    del_center = Vaccination_Center.query.filter_by(id=id).first()
    db.session.delete(del_center)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()

    # Run the Flask application
    app.run(debug=True)
