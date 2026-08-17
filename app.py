from flask import Flask, redirect, render_template, request, url_for

from database import get_connection

app = Flask(__name__)
app.secret_key = "hospital123"


@app.route('/get-doctor/<int:doctor_id>')
def get_doctor(doctor_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM doctors WHERE doctor_id = %s",
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    if doctor:
        return doctor

    return {"error": "Doctor not found"}, 404


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE username = %s
        AND password = %s
        AND role = %s
        """

        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            if role == "admin":
                return redirect(url_for("admin_dashboard"))

            elif role == "doctor":
                return redirect(url_for("doctors"))

            elif role == "receptionist":
                return redirect(url_for("appointments"))

        return render_template(
            "login.html",
            error="Invalid username, password or role."
        )

    return render_template("login.html")


@app.route("/admin-dashboard")
def admin_dashboard():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Patients
    cursor.execute("SELECT COUNT(*) AS total_patients FROM patients")
    total_patients = cursor.fetchone()["total_patients"]

    # Total Doctors
    cursor.execute("SELECT COUNT(*) AS total_doctors FROM doctors")
    total_doctors = cursor.fetchone()["total_doctors"]

    # Total Appointments
    cursor.execute("SELECT COUNT(*) AS total_appointments FROM appointments")
    total_appointments = cursor.fetchone()["total_appointments"]

    # Total Revenue
    cursor.execute(
        "SELECT SUM(total_amount) AS revenue FROM billing"
    )
    result = cursor.fetchone()

    revenue = result["revenue"] if result["revenue"] else 0

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        revenue=revenue,
    )


@app.route("/patients")
def patients():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("patients.html", patients=patients)


@app.route("/add-patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        disease = request.form["disease"]
        doctor_assigned = request.form["doctor_assigned"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO patients (
            patient_name,
            age,
            gender,
            phone,
            address,
            disease,
            doctor_assigned,
            status
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        values = (
            patient_name,
            age,
            gender,
            phone,
            address,
            disease,
            doctor_assigned,
            status,
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("patients"))

    return render_template("add_patient.html")


@app.route("/edit-patient/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):

    conn = get_connection()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        disease = request.form["disease"]
        doctor_assigned = request.form["doctor_assigned"]
        status = request.form["status"]

        cursor = conn.cursor()

        query = """
        UPDATE patients
        SET
            patient_name = %s,
            age = %s,
            gender = %s,
            phone = %s,
            address = %s,
            disease = %s,
            doctor_assigned = %s,
            status = %s
        WHERE patient_id = %s
        """

        values = (
            patient_name,
            age,
            gender,
            phone,
            address,
            disease,
            doctor_assigned,
            status,
            patient_id,
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("patients"))

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM patients WHERE patient_id = %s",
        (patient_id,),
    )

    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    if not patient:
        return "Patient not found", 404

    return render_template(
        "edit_patient.html",
        patient=patient,
    )


@app.route("/delete-patient/<int:patient_id>")
def delete_patient(patient_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE patient_id = %s",
        (patient_id,),
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("patients"))


@app.route("/doctors")
def doctors():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("doctors.html", doctors=doctors)


@app.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():

    if request.method == "POST":

        doctor_name = request.form["doctor_name"]
        specialization = request.form["specialization"]
        qualification = request.form["qualification"]
        phone = request.form["phone"]
        email = request.form["email"]
        experience = request.form["experience"]
        department = request.form["department"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO doctors
        (
            doctor_name,
            specialization,
            qualification,
            phone,
            email,
            experience,
            department,
            status
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            doctor_name,
            specialization,
            qualification,
            phone,
            email,
            experience,
            department,
            status
        )

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("doctors"))

    return render_template("add_doctor.html")


@app.route(
    "/edit-doctor/<int:doctor_id>",
    methods=["GET", "POST"],
)
def edit_doctor(doctor_id):

    conn = get_connection()

    if request.method == "POST":

        doctor_name = request.form["doctor_name"]
        specialization = request.form["specialization"]
        qualification = request.form["qualification"]
        phone = request.form["phone"]
        email = request.form["email"]
        experience = request.form["experience"]
        department = request.form["department"]
        status = request.form["status"]

        cursor = conn.cursor()

        query = """
        UPDATE doctors
        SET
            doctor_name = %s,
            specialization = %s,
            qualification = %s,
            phone = %s,
            email = %s,
            experience = %s,
            department = %s,
            status = %s
        WHERE doctor_id = %s
        """

        values = (
            doctor_name,
            specialization,
            qualification,
            phone,
            email,
            experience,
            department,
            status,
            doctor_id,
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("doctors"))

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM doctors
        WHERE doctor_id = %s
        """,
        (doctor_id,),
    )

    doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    if not doctor:
        return "Doctor not found", 404

    return render_template(
        "edit_doctor.html",
        doctor=doctor,
    )


@app.route("/delete-doctor/<int:doctor_id>")
def delete_doctor(doctor_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM doctors WHERE doctor_id = %s",
        (doctor_id,),
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("doctors"))


@app.route("/appointments")
def appointments():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments
    )


@app.route("/receptionists")
def receptionists():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM receptionists")
    receptionists = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "receptionists.html",
        receptionists=receptionists
    )


@app.route("/add-receptionist", methods=["GET", "POST"])
def add_receptionist():

    if request.method == "POST":

        receptionist_name = request.form["receptionist_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        shift = request.form["shift"]
        username = request.form["username"]
        password = request.form["password"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO receptionists
        (
            receptionist_name,
            phone,
            email,
            shift,
            username,
            password,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            receptionist_name,
            phone,
            email,
            shift,
            username,
            password,
            status
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("receptionists"))

    return render_template("add_receptionist.html")


@app.route("/billing")
def billing():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM billing")
    bills = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("billing.html", bills=bills)


@app.route("/add-bill", methods=["GET", "POST"])
def add_bill():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        consultation_fee = float(request.form["consultation_fee"])
        medicine_fee = float(request.form["medicine_fee"])
        lab_fee = float(request.form["lab_fee"])

        total_amount = consultation_fee + medicine_fee + lab_fee

        payment_status = request.form["payment_status"]
        bill_date = request.form["bill_date"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO billing
        (
            patient_name,
            doctor_name,
            consultation_fee,
            medicine_fee,
            lab_fee,
            total_amount,
            payment_status,
            bill_date
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            patient_name,
            doctor_name,
            consultation_fee,
            medicine_fee,
            lab_fee,
            total_amount,
            payment_status,
            bill_date
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("billing"))

    return render_template("add_bill.html")


@app.route("/reports")
def reports():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_patients FROM patients")
    total_patients = cursor.fetchone()["total_patients"]

    cursor.execute("SELECT COUNT(*) AS total_doctors FROM doctors")
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute("SELECT COUNT(*) AS total_appointments FROM appointments")
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute(
        "SELECT SUM(total_amount) AS total_revenue FROM billing"
    )
    revenue = cursor.fetchone()["total_revenue"]

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        revenue=revenue or 0
    )


@app.route("/medical-history")
def medical_history():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM medical_history")
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "medical_history.html",
        records=records
    )


@app.route("/add-medical-history", methods=["GET", "POST"])
def add_medical_history():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        diagnosis = request.form["diagnosis"]
        treatment = request.form["treatment"]
        medicines = request.form["medicines"]
        visit_date = request.form["visit_date"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO medical_history
        (
            patient_name,
            doctor_name,
            diagnosis,
            treatment,
            medicines,
            visit_date
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            patient_name,
            doctor_name,
            diagnosis,
            treatment,
            medicines,
            visit_date
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("medical_history"))

    return render_template("add_medical_history.html")


@app.route("/prescriptions")
def prescriptions():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM prescriptions")
    prescriptions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "prescriptions.html",
        prescriptions=prescriptions
    )


@app.route("/add-prescription", methods=["GET", "POST"])
def add_prescription():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        medicines = request.form["medicines"]
        dosage = request.form["dosage"]
        instructions = request.form["instructions"]
        prescription_date = request.form["prescription_date"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO prescriptions
        (
            patient_name,
            doctor_name,
            medicines,
            dosage,
            instructions,
            prescription_date
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            patient_name,
            doctor_name,
            medicines,
            dosage,
            instructions,
            prescription_date
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("prescriptions"))

    return render_template("add_prescription.html")


@app.route("/lab-reports")
def lab_reports():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM lab_reports")
    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("lab_reports.html", reports=reports)


@app.route("/add-lab-report", methods=["GET", "POST"])
def add_lab_report():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        test_name = request.form["test_name"]
        result = request.form["result"]
        report_date = request.form["report_date"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO lab_reports
        (
            patient_name,
            doctor_name,
            test_name,
            result,
            report_date,
            status
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            patient_name,
            doctor_name,
            test_name,
            result,
            report_date,
            status
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("lab_reports"))

    return render_template("add_lab_report.html")


@app.route("/notifications")
def notifications():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM notifications
        ORDER BY notification_date DESC
    """)

    notifications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )


@app.route("/add-notification", methods=["GET", "POST"])
def add_notification():

    if request.method == "POST":

        title = request.form["title"]
        message = request.form["message"]
        notification_date = request.form["notification_date"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO notifications
        (
            title,
            message,
            notification_date,
            status
        )
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(query, (
            title,
            message,
            notification_date,
            status
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("notifications"))

    return render_template("add_notification.html")


@app.route("/add-appointment", methods=["GET", "POST"])
def add_appointment():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        department = request.form["department"]

        return redirect(
            url_for(
                "select_doctor",
                department=department,
                patient_name=patient_name,
                age=age,
                gender=gender,
                phone=phone,
                address=address
            )
        )

    return render_template("add_appointment.html")


@app.route("/select-doctor")
def select_doctor():

    department = request.args.get("department")

    patient_name = request.args.get("patient_name")
    age = request.args.get("age")
    gender = request.args.get("gender")
    phone = request.args.get("phone")
    address = request.args.get("address")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            doctor_id,
            doctor_name,
            specialization,
            phone,
            email,
            experience,
            qualification,
            department,
            status,
            photo
        FROM doctors
        WHERE department = %s
        ORDER BY doctor_name
        """,
        (department,)
    )

    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "select_doctor.html",
        doctors=doctors,
        department=department,
        patient_name=patient_name,
        age=age,
        gender=gender,
        phone=phone,
        address=address
    )


@app.route("/confirm-doctor", methods=["POST"])
def confirm_doctor():

    doctor_id = request.form["doctor_id"]
    department = request.form["department"]

    patient_name = request.form["patient_name"]
    age = request.form["age"]
    gender = request.form["gender"]
    phone = request.form["phone"]
    address = request.form["address"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            doctor_id,
            doctor_name,
            specialization,
            phone,
            email,
            experience,
            qualification,
            department,
            status,
            photo
        FROM doctors
        WHERE doctor_id = %s
        """,
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    if not doctor:
        return "Doctor not found"

    return render_template(
        "appointment_details.html",
        doctor=doctor,
        department=department,
        patient_name=patient_name,
        age=age,
        gender=gender,
        phone=phone,
        address=address
    )


@app.route("/save-appointment", methods=["POST"])
def save_appointment():

    patient_name = request.form["patient_name"]
    age = request.form["age"]
    gender = request.form["gender"]
    phone = request.form["phone"]
    address = request.form["address"]

    doctor_id = request.form["doctor_id"]
    department = request.form["department"]

    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]

    # Automatically set appointment status
    status = "Scheduled"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT doctor_name
        FROM doctors
        WHERE doctor_id = %s
        """,
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    if not doctor:
        cursor.close()
        conn.close()
        return "Doctor not found"

    doctor_name = doctor["doctor_name"]

    cursor.close()

    cursor = conn.cursor()

    query = """
    INSERT INTO appointments
    (
        patient_name,
        age,
        gender,
        phone,
        address,
        doctor_name,
        appointment_date,
        appointment_time,
        department,
        status
    )
    VALUES
    (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    """

    values = (
        patient_name,
        age,
        gender,
        phone,
        address,
        doctor_name,
        appointment_date,
        appointment_time,
        department,
        status
    )

    cursor.execute(query, values)

    conn.commit()

    cursor.close()
    conn.close()

    return render_template("appointment_success.html")


@app.route("/delete-appointment/<int:appointment_id>")
def delete_appointment(appointment_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM appointments WHERE appointment_id = %s",
        (appointment_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("appointments"))


@app.route(
    "/edit-appointment/<int:appointment_id>",
    methods=["GET", "POST"]
)
def edit_appointment(appointment_id):

    conn = get_connection()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        department = request.form["department"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        status = request.form["status"]

        cursor = conn.cursor()

        query = """
        UPDATE appointments
        SET
            patient_name = %s,
            doctor_name = %s,
            appointment_date = %s,
            appointment_time = %s,
            department = %s,
            age = %s,
            gender = %s,
            phone = %s,
            address = %s,
            status = %s
        WHERE appointment_id = %s
        """

        values = (
            patient_name,
            doctor_name,
            appointment_date,
            appointment_time,
            department,
            age,
            gender,
            phone,
            address,
            status,
            appointment_id,
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("appointments"))

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM appointments
        WHERE appointment_id = %s
        """,
        (appointment_id,)
    )

    appointment = cursor.fetchone()

    cursor.close()
    conn.close()

    if not appointment:
        return "Appointment not found", 404

    return render_template(
        "edit_appointment.html",
        appointment=appointment
    )


if __name__ == "__main__":
    app.run(debug=True)
