import pandas as pd
import matplotlib.pyplot as plt
import os

filename = 'data.csv' # makes sure the life exists

def load_data(filename):
  """Load data from csv file"""
  if not os.path.exists(filename):
    print(f"Error: File '{filename}' not found!")
    exit(1)
  
  df = pd.read_csv(filename)
  df.columns = df.columns.str.lower()
  return df

def calculate_gpa(df):
  """Calculates the gpa"""
  df['gpa'] = df['grade'] / 25
  
  overall_gpa = df.groupby(['student_id', 'name']).agg({
    'grade': 'mean',
    'gpa': 'mean'
  }).reset_index()
  return overall_gpa

def ranking(df):
  """Ranks based on GPA"""
  df['rank'] = df['gpa'].rank(ascending=False, method='dense')
  ranked_df = df.sort_values('rank')
  return ranked_df

def student_at_risk(df):
  """Identifies students which grades < 60"""
  risk = df[df['grade'] < 60][['student_id', 'name']].drop_duplicates()
  return risk

def class_report(df, ranked_students):
  """Generates class report"""
  class_average = df['grade'].mean()

  report_dict = {
     "Class_average": round(class_average, 1),
     "Top_student": ranked_students.iloc[0]['name'],
     "Top_grade": round(ranked_students.iloc[0]['grade'], 1),
     "Top_gpa" : round(ranked_students.iloc[0]['gpa'], 2),
     "Bottom_student": ranked_students.iloc[-1]['name'],
     "Bottom_grade": round(ranked_students.iloc[-1]['grade'], 1),
     "Bottom_gpa" : round(ranked_students.iloc[-1]['gpa'], 2),
     "Total_students": len(df['student_id'].unique()),
     "Number_at_risk": len(student_at_risk(df))
  }
  return report_dict

def individual_reports(ranked_students):
  """Generated individual reports"""
  reports = ranked_students.copy()

  reports['performance'] = reports['grade'].apply(
    lambda g: 'At Risk' if g < 60 else
              'Needs to work harder' if g < 70 else
              'satisfactory' if g < 80 else
              'Good' if g < 90 else 'Excellent'
  )

  reports['grade'] = reports['grade'].round(1)
  reports['gpa'] = reports['gpa'].round(2)
  reports['rank'] = reports['rank'].astype(int)

  
  reports = reports[['student_id', 'name', 'grade', 'gpa', 'rank', 'performance']]
  return reports

def save_reports(class_report_dict, individual_df):
  """Saves reports to files"""
  
  with open('class_report.txt', 'w') as f:
    for key, value in class_report_dict.items():
      f.write(f"{key}: {value}\n")
  
  individual_df.to_csv('individual_reports.csv', index=False)
  
  at_risk = individual_df[individual_df['performance'] == 'At Risk']
  if not at_risk.empty:
    at_risk[['name', 'grade']].to_csv('at_risk_students.csv', index=False)

def student_data_hist(df):
  """Creates Histogram for students data"""
  plt.hist(df['grade'], bins=20, edgecolor='black')
  plt.title("Student Grade Distribution")
  plt.xlabel("Grade")
  plt.ylabel("Number of Students")
  plt.show()

def write_recommendation(student_at_risk_df):
  """Writes a reccomendation for at risk students to a file"""
  if student_at_risk_df.empty:
    print("No at_risk students to write recommendations for.")
    return
  
  with open("recommendation.txt", "w") as f:
    for index, student in student_at_risk_df.iterrows():
      f.write(f"Student {student['name']} needs academic support.\n")
  print("Recommendations written to 'recommendation.txt'")

def main():
  # load data
  df = load_data(filename)

  # Calculate gpa
  overall_gpa = calculate_gpa(df)
  print("Gpa DataFrame:")
  print(overall_gpa)
  
  #Rank students
  ranked_students = ranking(overall_gpa)
  print("\n\nRanked Students:")
  print(ranked_students)

  # identify students that need help
  at_risk = student_at_risk(df)
  print("\n\nStudents at Risk:")
  print(at_risk)

  # generate report
  report_for_class = class_report(df, ranked_students)
  individual_df = individual_reports(ranked_students)

  # save reports to files
  save_reports(report_for_class, individual_df)

  print("\n\nClass Report:")
  for key, value in report_for_class.items():
    print(f"{key}: {value}")

  print("\n\nIndividual Reports (first 5):")
  print(individual_df.head())

  print("\n\nAt-Risk Students:")
  at_risk_individual = individual_df[individual_df['performance'] == 'At Risk']
  print(at_risk_individual[['name', 'grade', 'performance']].to_string(index=False))

  # visualize data
  student_data_hist(df)

  # write recommendations
  write_recommendation(at_risk)

  print("\n\nFiles created: class_report.txt, individual_reports.csv, at_risk_students.csv, recommendation.txt")

if __name__ == "__main__":
   main()
