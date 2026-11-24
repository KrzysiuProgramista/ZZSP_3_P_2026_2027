# Librus Intelligence

Run python install.py from this folder. Python 3.10+ is required. The installer creates files next to itself, skips existing files, and installs dependencies in a local .venv. Package installation requires internet; personal records are not uploaded.

Run the generated run.py using python run.py. For fictional data: python run.py --csv sample_grades.csv

Inspect your own PDF: python run.py --inspect "path/to/export.pdf"
Review private_work locally and manually create grades.csv with columns date,subject,grade,description. Dates should be YYYY-MM-DD. Then use python run.py.

Run tests: python run.py --test

Do not commit or submit your PDF, grades.csv, private_work, or screenshots with personal records. Git ignore rules are not protection for files already tracked. Do not force-add private files. Submit only code and the anonymous report.
