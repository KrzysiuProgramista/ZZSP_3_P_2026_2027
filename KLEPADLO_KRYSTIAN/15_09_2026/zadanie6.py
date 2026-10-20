
import pandas as pd

# Create the DataFrame
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)

# Add a column 'average' with each student's mean across the three subjects
df_grades['average'] = df_grades[['maths', 'physics', 'english']].mean(axis=1)

# Add a column 'passed' that is True when the average is at least 3.0
df_grades['passed'] = df_grades['average'] >= 3.0

# Add a column 'best_subject' naming the subject with their highest grade
df_grades['best_subject'] = df_grades[['maths', 'physics', 'english']].idxmax(axis=1)

# Print the table sorted by average, descending
print(df_grades.sort_values(by='average', ascending=False))
