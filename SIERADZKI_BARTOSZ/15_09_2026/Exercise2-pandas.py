import io
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}


def exercise_2():
    df_grades = pd.DataFrame(data)

    print("=== df_grades ===")
    print(df_grades)

    print("\n=== df_grades.shape ===")
    print(df_grades.shape)

    print("\n=== df_grades.columns ===")
    print(df_grades.columns)

    print("\n=== df_grades.index ===")
    print(df_grades.index)

    print("\n=== df_grades.dtypes ===")
    print(df_grades.dtypes)

    # df_grades.info() prints to stdout in older pandas, but returns None in
    # pandas 3.x. Capture its text in a StringIO buffer, then print line by line.
    buf = io.StringIO()
    df_grades.info(buf=buf)
    info_text = buf.getvalue()
    print("\n=== df_grades.info() ===")
    for line in info_text.splitlines():
        print(line)

    print("\n=== df_grades.describe() ===")
    print(df_grades.describe())


if __name__ == "__main__":
    exercise_2()
