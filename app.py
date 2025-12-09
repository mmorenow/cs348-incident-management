from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/incidents')
def incidents():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT i.*, u.name as user_name
        FROM incidents i
        LEFT JOIN users u ON i.user_id = u.id
        ORDER BY i.date DESC
    ''')
    incidents = cursor.fetchall()

    cursor.execute('SELECT DISTINCT severity FROM incidents')
    severities = cursor.fetchall()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('incidents.html', incidents=incidents, severities=severities, users=users)

@app.route('/incidents/create', methods=['POST'])
def create_incident():
    incident_type = request.form['type']
    severity = request.form['severity']
    status = request.form['status']
    date = request.form['date']
    description = request.form['description']
    user_id = request.form.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO incidents (type, severity, status, date, description, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (incident_type, severity, status, date, description, user_id if user_id else None))

        conn.commit()
        
    except Exception as e:

        conn.rollback()
        print(f"Error creating incident: {e}")
        raise
        
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('incidents'))

# UPDATE INCIDENT
@app.route('/incidents/update/<int:id>', methods=['GET', 'POST'])
def update_incident(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':

        cursor.execute('SELECT * FROM incidents WHERE id = %s', (id,))
        incident = cursor.fetchone()
        
 
        cursor.execute('SELECT DISTINCT severity FROM incidents')
        severities = cursor.fetchall()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('update_incident.html', 
                             incident=incident, 
                             severities=severities,
                             users=users)

    elif request.method == 'POST':
        incident_type = request.form['type']
        severity = request.form['severity']
        status = request.form['status']
        date = request.form['date']
        description = request.form['description']
        user_id = request.form.get('user_id')

        try:
            cursor.execute('''
                UPDATE incidents 
                SET type = %s, severity = %s, status = %s, date = %s, description = %s, user_id = %s
                WHERE id = %s
            ''', (incident_type, severity, status, date, description, user_id if user_id else None, id))


            conn.commit()
            
        except Exception as e:

            conn.rollback()
            print(f"Error updating incident: {e}")
            raise
            
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('incidents'))

# DELETE INCIDENT
@app.route('/incidents/delete/<int:id>')
def delete_incident(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM incidents WHERE id = %s', (id,))
        

        conn.commit()
        
    except Exception as e:

        conn.rollback()
        print(f"Error deleting incident: {e}")
        raise
        
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('incidents'))

@app.route('/report')
def report():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    incident_type = request.args.get('type', '')
    user_id = request.args.get('user_id', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM incidents WHERE 1=1'
    params = []

    if start_date:
        query += ' AND date >= %s'
        params.append(start_date)

    if end_date:
        query += ' AND date <= %s'
        params.append(end_date)

    if severity:
        query += ' AND severity = %s'
        params.append(severity)

    if status:
        query += ' AND status = %s'
        params.append(status)

    if incident_type:
        query += ' AND type = %s'
        params.append(incident_type)

    if user_id:
        query += ' AND user_id = %s'
        params.append(user_id)

    query += ' ORDER BY date DESC'

    cursor.execute(query, params)
    incidents = cursor.fetchall()

    total_incidents = len(incidents)

    severity_counts = {}
    for incident in incidents:
        sev = incident['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    status_counts = {}
    for incident in incidents:
        stat = incident['status']
        status_counts[stat] = status_counts.get(stat, 0) + 1

    cursor.execute('SELECT DISTINCT type FROM incidents')
    types = cursor.fetchall()
    
    cursor.execute('SELECT DISTINCT severity FROM incidents')
    severities = cursor.fetchall()
    
    cursor.execute('SELECT DISTINCT status FROM incidents')
    statuses = cursor.fetchall()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('report.html',
                           incidents=incidents,
                           total_incidents=total_incidents,
                           severity_counts=severity_counts,
                           status_counts=status_counts,
                           types=types,
                           severities=severities,
                           statuses=statuses,
                           users=users,
                           current_start_date=start_date,
                           current_end_date=end_date,
                           current_severity=severity,
                           current_status=status,
                           current_type=incident_type,
                           current_user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
