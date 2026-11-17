import pandas as pd

# Re-creating df_grades and including the student column for easy manipulation
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)

print("=========================================")
print("       Exercise 6: Adding New Columns      ")
print("=========================================\n")

# --- Task Execution ---

# 1. Add 'average' column (mean across subjects/axis=1)
df_grades['average'] = df_grades[['maths', 'physics', 'english']].mean(axis=1)

# 2. Add 'passed' column (Boolean check on average >= 3.0)
df_grades['passed'] = df_grades['average'] >= 3.0

# 3. Add 'best_subject' column (Subject with highest grade using idxmax on axis=1)
# This requires finding which *column* has the max value across the row (axis=1)
highest_grade_col = df_grades[['maths', 'physics', 'english']].idxmax(axis=1)
df_grades['best_subject'] = highest_grade_col

# 4. Print the table sorted by average, descending
print("\n--- Final DataFrame Sorted by Average (Descending) ---")
# Sort the final result to display findings clearly
final_sorted_df = df_grades.sort_values(by='average', ascending=False)
print(final_sorted_df.to_string())