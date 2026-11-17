import pandas as pd

# Re-creating df_grades from Exercise 2
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)

print("=========================================")
print("       Exercise 5: Answers in One Expression     ")
print("=========================================\n")

# --- Answering the questions using ONE pandas expression each ---

# 1. What is the class average in maths?
avg_maths = df_grades["maths"].mean()

# 2. Who scored highest in physics? (hint: idxmax)
highest_physics_student = df_grades["physics"].idxmax()

# 3. What is each student's average across the three subjects? (hint: axis=1)
student_averages = df_grades.mean(axis=1).to_dict()

# 4. How many students scored 5 in english?
count_english_fives = (df_grades["english"] == 5).sum()

# 5. What is the average of all grades in the whole table?
grand_average = df_grades.values.mean()

# Display Results (since the prompt implies execution and observation)
print("--- Question 1: Class average in maths? ---")
print(avg_maths)

print("\n--- Question 2: Student with highest physics score? ---")
# The result is an index label (e.g., 'Ola') which corresponds to the student name in this setup
print(highest_physics_student) 

print("\n--- Question 3: Each student's average? ---")
# Displaying the result clearly mapping index (student) to value (average)
for student, avg in student_averages.items():
    print(f"{student}: {avg}")

print("\n--- Question 4: Count of students with English grade of 5? ---")
print(count_english_fives)

print("\n--- Question 5: Overall average of all grades? ---")
print(grand_average)