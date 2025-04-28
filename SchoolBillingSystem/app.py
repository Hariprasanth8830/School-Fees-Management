import os
import logging
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import uuid
from datetime import datetime
from utils import ensure_data_files, load_data, save_data, generate_bill_number

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Context processor to make 'now' available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Ensure data directories and files exist
ensure_data_files()

# Routes
@app.route('/')
def index():
    """Dashboard/homepage showing summary data"""
    students = load_data('students.json')
    bills = load_data('bills.json')
    fees = load_data('fees.json')
    payments = load_data('payments.json')
    
    # Summary statistics
    total_students = len(students)
    total_bills = len(bills)
    total_fee_types = len(fees)
    
    # Calculate total amount billed and received
    total_billed = sum(float(bill.get('total_amount', 0)) for bill in bills)
    total_received = sum(float(payment.get('amount', 0)) for payment in payments)
    
    # Get recent bills (last 5)
    recent_bills = sorted(bills, key=lambda x: x.get('date', ''), reverse=True)[:5]
    
    # Get unpaid bills
    unpaid_bills = [bill for bill in bills if bill.get('status') == 'Unpaid']
    total_unpaid = sum(float(bill.get('total_amount', 0)) for bill in unpaid_bills)
    
    return render_template('index.html', 
                           total_students=total_students,
                           total_bills=total_bills,
                           total_fee_types=total_fee_types,
                           total_billed=total_billed,
                           total_received=total_received,
                           total_unpaid=total_unpaid,
                           recent_bills=recent_bills,
                           unpaid_bills=unpaid_bills)

# Student Management Routes
@app.route('/students')
def students():
    """Display the list of students"""
    students = load_data('students.json')
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        # Get form data
        student_id = str(uuid.uuid4())
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        section = request.form.get('section')
        roll_number = request.form.get('roll_number')
        admission_number = request.form.get('admission_number')
        parent_name = request.form.get('parent_name')
        contact_number = request.form.get('contact_number')
        address = request.form.get('address')
        
        # Validate required fields
        if not all([name, class_name, admission_number, parent_name, contact_number]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('add_student'))
        
        # Create student object
        new_student = {
            'id': student_id,
            'name': name,
            'class_name': class_name,
            'section': section,
            'roll_number': roll_number,
            'admission_number': admission_number,
            'parent_name': parent_name,
            'contact_number': contact_number,
            'address': address,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Load existing students
        students = load_data('students.json')
        
        # Check if admission number already exists
        if any(s.get('admission_number') == admission_number for s in students):
            flash('A student with this admission number already exists', 'danger')
            return redirect(url_for('add_student'))
        
        # Add new student
        students.append(new_student)
        
        # Save updated students list
        save_data('students.json', students)
        
        flash('Student added successfully', 'success')
        return redirect(url_for('students'))
    
    return render_template('student_form.html', student=None, action='add')

@app.route('/students/edit/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit an existing student"""
    students = load_data('students.json')
    student = next((s for s in students if s.get('id') == student_id), None)
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))
    
    if request.method == 'POST':
        # Update student data
        student['name'] = request.form.get('name')
        student['class_name'] = request.form.get('class_name')
        student['section'] = request.form.get('section')
        student['roll_number'] = request.form.get('roll_number')
        student['admission_number'] = request.form.get('admission_number')
        student['parent_name'] = request.form.get('parent_name')
        student['contact_number'] = request.form.get('contact_number')
        student['address'] = request.form.get('address')
        student['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save updated students list
        save_data('students.json', students)
        
        flash('Student updated successfully', 'success')
        return redirect(url_for('students'))
    
    return render_template('student_form.html', student=student, action='edit')

@app.route('/students/delete/<student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete a student"""
    students = load_data('students.json')
    updated_students = [s for s in students if s.get('id') != student_id]
    
    if len(updated_students) == len(students):
        flash('Student not found', 'danger')
    else:
        # Save updated students list
        save_data('students.json', updated_students)
        flash('Student deleted successfully', 'success')
    
    return redirect(url_for('students'))

# Fee Structure Management Routes
@app.route('/fees')
def fees():
    """Display the list of fee structures"""
    fees = load_data('fees.json')
    return render_template('fees.html', fees=fees)

@app.route('/fees/add', methods=['GET', 'POST'])
def add_fee():
    """Add a new fee structure"""
    if request.method == 'POST':
        # Get form data
        fee_id = str(uuid.uuid4())
        name = request.form.get('name')
        amount = request.form.get('amount')
        class_applicable = request.form.get('class_applicable')
        frequency = request.form.get('frequency')
        description = request.form.get('description')
        
        # Validate required fields
        if not all([name, amount, frequency]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('add_fee'))
        
        # Create fee object
        new_fee = {
            'id': fee_id,
            'name': name,
            'amount': float(amount),
            'class_applicable': class_applicable,
            'frequency': frequency,
            'description': description,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Load existing fees
        fees = load_data('fees.json')
        
        # Add new fee
        fees.append(new_fee)
        
        # Save updated fees list
        save_data('fees.json', fees)
        
        flash('Fee structure added successfully', 'success')
        return redirect(url_for('fees'))
    
    return render_template('fee_form.html', fee=None, action='add')

@app.route('/fees/edit/<fee_id>', methods=['GET', 'POST'])
def edit_fee(fee_id):
    """Edit an existing fee structure"""
    fees = load_data('fees.json')
    fee = next((f for f in fees if f.get('id') == fee_id), None)
    
    if not fee:
        flash('Fee structure not found', 'danger')
        return redirect(url_for('fees'))
    
    if request.method == 'POST':
        # Update fee data
        fee['name'] = request.form.get('name')
        fee['amount'] = float(request.form.get('amount'))
        fee['class_applicable'] = request.form.get('class_applicable')
        fee['frequency'] = request.form.get('frequency')
        fee['description'] = request.form.get('description')
        fee['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save updated fees list
        save_data('fees.json', fees)
        
        flash('Fee structure updated successfully', 'success')
        return redirect(url_for('fees'))
    
    return render_template('fee_form.html', fee=fee, action='edit')

@app.route('/fees/delete/<fee_id>', methods=['POST'])
def delete_fee(fee_id):
    """Delete a fee structure"""
    fees = load_data('fees.json')
    updated_fees = [f for f in fees if f.get('id') != fee_id]
    
    if len(updated_fees) == len(fees):
        flash('Fee structure not found', 'danger')
    else:
        # Save updated fees list
        save_data('fees.json', updated_fees)
        flash('Fee structure deleted successfully', 'success')
    
    return redirect(url_for('fees'))

# Bill Management Routes
@app.route('/bills')
def bills():
    """Display the list of bills"""
    bills = load_data('bills.json')
    students = load_data('students.json')
    
    # Create a mapping of student IDs to names for easier display
    student_names = {s.get('id'): s.get('name') for s in students}
    
    return render_template('bills.html', bills=bills, student_names=student_names)

@app.route('/bills/generate', methods=['GET', 'POST'])
def generate_bill():
    """Generate a new bill"""
    students = load_data('students.json')
    fees = load_data('fees.json')
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # Get form data
        bill_id = str(uuid.uuid4())
        student_id = request.form.get('student_id')
        bill_date = request.form.get('bill_date')
        due_date = request.form.get('due_date')
        
        # Get selected fee IDs
        fee_ids = request.form.getlist('fee_ids')
        
        # Validate required fields
        if not all([student_id, bill_date, due_date]) or not fee_ids:
            flash('Please fill in all required fields and select at least one fee', 'danger')
            return redirect(url_for('generate_bill'))
        
        # Generate bill details
        bill_number = generate_bill_number()
        
        # Calculate total amount
        total_amount = 0
        bill_items = []
        
        for fee_id in fee_ids:
            fee = next((f for f in fees if f.get('id') == fee_id), None)
            if fee:
                amount = float(fee.get('amount', 0))
                total_amount += amount
                bill_items.append({
                    'fee_id': fee_id,
                    'fee_name': fee.get('name'),
                    'amount': amount
                })
        
        # Get student details
        student = next((s for s in students if s.get('id') == student_id), None)
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('generate_bill'))
        
        # Create bill object
        new_bill = {
            'id': bill_id,
            'bill_number': bill_number,
            'student_id': student_id,
            'date': bill_date,
            'due_date': due_date,
            'items': bill_items,
            'total_amount': total_amount,
            'status': 'Unpaid',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Load existing bills
        bills = load_data('bills.json')
        
        # Add new bill
        bills.append(new_bill)
        
        # Save updated bills list
        save_data('bills.json', bills)
        
        flash('Bill generated successfully', 'success')
        return redirect(url_for('view_bill', bill_id=bill_id))
    
    return render_template('generate_bill.html', students=students, fees=fees, today_date=today_date)

@app.route('/bills/view/<bill_id>')
def view_bill(bill_id):
    """View a bill"""
    bills = load_data('bills.json')
    students = load_data('students.json')
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    bill = next((b for b in bills if b.get('id') == bill_id), None)
    
    if not bill:
        flash('Bill not found', 'danger')
        return redirect(url_for('bills'))
    
    student = next((s for s in students if s.get('id') == bill.get('student_id')), None)
    
    if not student:
        flash('Student associated with this bill not found', 'danger')
        return redirect(url_for('bills'))
    
    return render_template('bill_print.html', bill=bill, student=student, today_date=today_date)

@app.route('/bills/update_status/<bill_id>', methods=['POST'])
def update_bill_status(bill_id):
    """Update bill payment status"""
    bills = load_data('bills.json')
    bill = next((b for b in bills if b.get('id') == bill_id), None)
    
    if not bill:
        flash('Bill not found', 'danger')
        return redirect(url_for('bills'))
    
    status = request.form.get('status')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method')
    
    # Update bill status
    bill['status'] = status
    bill['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # If marking as paid, create a payment record
    if status == 'Paid' and payment_date and payment_method:
        payment_id = str(uuid.uuid4())
        new_payment = {
            'id': payment_id,
            'bill_id': bill_id,
            'student_id': bill.get('student_id'),
            'amount': bill.get('total_amount'),
            'date': payment_date,
            'method': payment_method,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Load existing payments
        payments = load_data('payments.json')
        
        # Add new payment
        payments.append(new_payment)
        
        # Save updated payments list
        save_data('payments.json', payments)
    
    # Save updated bills list
    save_data('bills.json', bills)
    
    flash('Bill status updated successfully', 'success')
    return redirect(url_for('bills'))

@app.route('/bills/delete/<bill_id>', methods=['POST'])
def delete_bill(bill_id):
    """Delete a bill"""
    bills = load_data('bills.json')
    updated_bills = [b for b in bills if b.get('id') != bill_id]
    
    if len(updated_bills) == len(bills):
        flash('Bill not found', 'danger')
    else:
        # Save updated bills list
        save_data('bills.json', updated_bills)
        flash('Bill deleted successfully', 'success')
    
    return redirect(url_for('bills'))

# Payment Routes
@app.route('/payments')
def payments():
    """Display the list of payments"""
    payments = load_data('payments.json')
    students = load_data('students.json')
    bills = load_data('bills.json')
    
    # Create mappings for easier display
    student_names = {s.get('id'): s.get('name') for s in students}
    bill_numbers = {b.get('id'): b.get('bill_number') for b in bills}
    
    return render_template('payments.html', 
                           payments=payments, 
                           student_names=student_names,
                           bill_numbers=bill_numbers)

# Reporting Routes
@app.route('/reports')
def reports():
    """Display reports"""
    students = load_data('students.json')
    bills = load_data('bills.json')
    payments = load_data('payments.json')
    
    # Calculate statistics for reports
    total_billed = sum(float(bill.get('total_amount', 0)) for bill in bills)
    total_received = sum(float(payment.get('amount', 0)) for payment in payments)
    
    # Group bills by status
    paid_bills = [bill for bill in bills if bill.get('status') == 'Paid']
    unpaid_bills = [bill for bill in bills if bill.get('status') == 'Unpaid']
    
    # Calculate total amounts by status
    total_paid = sum(float(bill.get('total_amount', 0)) for bill in paid_bills)
    total_unpaid = sum(float(bill.get('total_amount', 0)) for bill in unpaid_bills)
    
    # Get student-wise billing summary
    student_summary = {}
    for bill in bills:
        student_id = bill.get('student_id')
        amount = float(bill.get('total_amount', 0))
        status = bill.get('status')
        
        if student_id not in student_summary:
            student = next((s for s in students if s.get('id') == student_id), None)
            student_name = student.get('name', 'Unknown') if student else 'Unknown'
            student_summary[student_id] = {
                'name': student_name,
                'total_billed': 0,
                'total_paid': 0,
                'total_unpaid': 0,
                'bill_count': 0
            }
        
        student_summary[student_id]['total_billed'] += amount
        student_summary[student_id]['bill_count'] += 1
        
        if status == 'Paid':
            student_summary[student_id]['total_paid'] += amount
        else:
            student_summary[student_id]['total_unpaid'] += amount
    
    # Convert to list for template
    student_summary_list = [
        {
            'student_id': student_id,
            'name': details['name'],
            'total_billed': details['total_billed'],
            'total_paid': details['total_paid'],
            'total_unpaid': details['total_unpaid'],
            'bill_count': details['bill_count']
        }
        for student_id, details in student_summary.items()
    ]
    
    return render_template('reports.html', 
                           total_billed=total_billed,
                           total_received=total_received,
                           total_paid=total_paid,
                           total_unpaid=total_unpaid,
                           paid_count=len(paid_bills),
                           unpaid_count=len(unpaid_bills),
                           student_summary=student_summary_list)

@app.route('/search')
def search():
    """Search for students or bills"""
    query = request.args.get('query', '').lower()
    
    if not query:
        return jsonify({'students': [], 'bills': []})
    
    students = load_data('students.json')
    bills = load_data('bills.json')
    
    # Search students
    student_results = []
    for student in students:
        if (query in student.get('name', '').lower() or
            query in student.get('admission_number', '').lower() or
            query in student.get('roll_number', '').lower()):
            student_results.append(student)
    
    # Search bills
    bill_results = []
    for bill in bills:
        if query in bill.get('bill_number', '').lower():
            # Add student name to bill result
            student_id = bill.get('student_id')
            student = next((s for s in students if s.get('id') == student_id), None)
            bill_with_student = bill.copy()
            bill_with_student['student_name'] = student.get('name', 'Unknown') if student else 'Unknown'
            bill_results.append(bill_with_student)
    
    return jsonify({'students': student_results, 'bills': bill_results})
