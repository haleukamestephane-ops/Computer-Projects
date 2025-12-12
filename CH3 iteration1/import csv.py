import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

GRADE_CONVERSION = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0
}

def load_student_data(filepath='stud_data.csv'):
    """Load student data from a CSV file and convert grades to grade points."""
    df = pd.read_csv(filepath)
    df['Grade_Points'] = df['Grade'].map(GRADE_CONVERSION)
    return df
    
def calculate_gpa(reader):
    """Calculate the GPA for each student (per semester)."""
    # ensure Grade_Points is mapped to letter grades
    if 'Grade_Points' not in reader.columns:
        reader = reader.copy()
        reader['Grade_Points'] = reader['Grade'].map(GRADE_CONVERSION)

    df = reader.copy()
    df['Weighted_Grade_Points'] = df['Grade_Points'] * df['Credits']

    gpa_data = df.groupby(['Student_ID', 'Name', 'Semester'], as_index=False).agg(
        {'Weighted_Grade_Points': 'sum', 'Credits': 'sum'}
    )
    gpa_data['GPA'] = gpa_data['Weighted_Grade_Points'] / gpa_data['Credits']
    gpa_data = gpa_data.rename(columns={'Credits': 'Semester_Credits'})
    return gpa_data[['Student_ID', 'Name', 'Semester', 'GPA', 'Semester_Credits']]

def class_rank(gpa_data):
    """Calculate Rank based gpa"""
    gpa_rank = gpa_data.sort_values('GPA', ascending=False)
    gpa_rank['Rank'] = range(1, len(gpa_rank) + 1)
    return gpa_rank

def students_at_risk(gpa_data):
    """Identify students at risk of failing."""
    at_risk_students = gpa_data[gpa_data['GPA'] < 2.0]
    return at_risk_students

def individual_report(student_id, gpa_data):
    """Generate an individual report for a student."""
    student_data = gpa_data[gpa_data['Student_ID'] == student_id]
    return student_data

def class_performance(gpa_data):
    """Generate class performance report."""
    performance_summary = gpa_data.groupby('Semester')['GPA'].agg(['mean', 'median', 'std']).reset_index()
    return performance_summary

def plot_gpa_trends(gpa_data, Name):
    """Plot GPA trends for a specific student."""
    student_graph_data = gpa_data[gpa_data['Name'] == Name].copy()
    if student_graph_data.empty:
        print(f'No GPA data found for student: {Name}')
        return

    # try to order semesters meaningfully: parse 'Term YYYY' like 'Fall 2024'
    def semester_key(s):
        if pd.isna(s):
            return (0, 0)
        s = str(s).strip()
        import re
        m = re.match(r"(?i)^(Spring|Summer|Fall|Winter)\s+(\d{4})$", s)
        if m:
            term, year = m.group(1).lower(), int(m.group(2))
            order = {'spring': 0, 'summer': 1, 'fall': 2, 'winter': 3}
            return (year, order.get(term, 9))
        # fallback: try parseable date
        try:
            dt = pd.to_datetime(s)
            return (dt.year, dt.month)
        except Exception:
            return (9999, 9)

    student_graph_data['__order'] = student_graph_data['Semester'].map(semester_key)
    student_graph_data = student_graph_data.sort_values('__order')

    x = range(len(student_graph_data))
    y = student_graph_data['GPA'].astype(float)
    labels = student_graph_data['Semester'].astype(str).tolist()

    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker='o')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.title(f'GPA Trends for {Name}')
    plt.xlabel('Semester')
    plt.ylabel('GPA')
    plt.ylim(0, 4)
    plt.grid()
    plt.tight_layout()
    plt.show()

def recommendations(at_risk_students):
    """Provide recommendations for at-risk students."""
    recommendations = {}
    for _, row in at_risk_students.iterrows():
        recommendations[row['Student_ID']] = f"Student {row['Name']} should consider seeking academic counseling and tutoring."
    return recommendations


if __name__ == '__main__':
    try:
        df = load_student_data()
    except Exception as e:
        print('Failed to load stud_data.csv:', e)
    else:
        print(f"Loaded {len(df)} rows from stud_data.csv")
        try:
            gpa = calculate_gpa(df)
        except Exception as e:
            print('Error calculating GPA:', e)
        else:
            print('\nSemester GPAs (sample):')
            print(gpa.head().to_string(index=False))

            ranks = class_rank(gpa)
            print('\nTop ranks (sample):')
            print(ranks.head().to_string(index=False))

            at_risk = students_at_risk(gpa)
            if at_risk.empty:
                print('\nNo at-risk students (GPA < 2.0)')
            else:
                print('\nAt-risk students:')
                print(at_risk.to_string(index=False))