import io
import warnings
warnings.simplefilter("always")
import pandas as pd

# 1. Create a DataFrame from a dictionary. The keys become the column names.
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)
print(df_grades)

# 2. Basic info about the DataFrame.
print(df_grades.shape)
print(df_grades.columns)
print(df_grades.index)
print(df_grades.dtypes)

# 3. df.info() prints to stdout, but in pandas >= 3 it returns None (no printing).
#    Redirect it into a StringIO buffer so it is captured as a string, then print
#    every line so the output is easy to read.
buf = io.StringIO()
df_grades.info(buf=buf)
info_lines = buf.getvalue().splitlines()
for line in info_lines:
    print(line)

# 4. df.describe() - a string in pandas 3.0+, print it directly.
print(df_grades.describe())
