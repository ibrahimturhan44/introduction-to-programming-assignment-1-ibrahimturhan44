import csv
import sqlite3



conn = sqlite3.connect("survey.db")
db = conn.cursor()


db.execute('''
CREATE TABLE IF NOT EXISTS responses (
    student_id TEXT,
    faculty TEXT,
    year INTEGER,
    satisfaction INTEGER,
    favourite_tool TEXT,
    comments TEXT
)
''')



csv_files = ["faculty_science.csv", "faculty_arts.csv", "faculty_business.csv"]

for filename in csv_files:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
               
                db.execute(
                    "INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        row['student_id'], 
                        row['faculty'], 
                        int(row['year']), 
                        int(row['satisfaction']), 
                        row['favourite_tool'], 
                        row['comments']
                    )
                )
    except FileNotFoundError:
        print(f"Hata: {filename} dosyası bulunamadı.")

conn.commit()
print("Database loaded successfully.\n")

print("-" * 30)
print("UNIVERSITY SURVEY DASHBOARD")
print("-" * 30)


print("\nn1. Total Responses by Faculty")
rows = db.execute("SELECT faculty, COUNT(*) FROM responses GROUP BY faculty ORDER BY faculty").fetchall()
total_all = 0
for row in rows:
    print(f"{row[0]:<10}: {row[1]}")
    total_all += row[1]
print(f"{'TOTAL':<10}: {total_all}")


print("\nn2. Average Satisfaction by Year of Study")
rows = db.execute("SELECT year, ROUND(AVG(satisfaction), 1) FROM responses GROUP BY year ORDER BY year").fetchall()
for row in rows:
    print(f"Year {row[0]} : {row[1]} / 5")


print("\nn3. Favourite Tool Popularity")
rows = db.execute("SELECT favourite_tool, COUNT(*) AS n FROM responses GROUP BY favourite_tool ORDER BY n DESC").fetchall()
for row in rows:
    print(f"{row[0]:>10} : {row[1]} students")


print("\nn4. Faculty Comparison")
print(f"{'Faculty':<12} | {'Avg Satisfaction':<18} | Most Popular Tool")
print("-" * 50)

faculties = ["Arts", "Business", "Science"]
for fac in faculties:
   
    avg_val = db.execute("SELECT ROUND(AVG(satisfaction), 1) FROM responses WHERE faculty = ?", (fac,)).fetchone()[0]
   
    top_tool = db.execute("SELECT favourite_tool FROM responses WHERE faculty = ? GROUP BY favourite_tool ORDER BY COUNT(*) DESC LIMIT 1", (fac,)).fetchone()
    
    tool_str = top_tool[0] if top_tool else "N/A"
    print(f"{fac:<12} | {avg_val if avg_val else 0:<18} | {tool_str}")


print()
try:
    min_score = int(input("Enter minimum satisfaction score (1-5): "))
   
    rows = db.execute(
        "SELECT student_id, faculty, year, favourite_tool FROM responses WHERE satisfaction >= ? ORDER BY faculty, year",
        (min_score,)
    ).fetchall()

    print(f"\nStudents with satisfaction >= {min_score}:")
    if not rows:
        print("No results found.")
    else:
        for row in rows:
            print(f" {row[0]} | {row[1]:<8} | Year {row[2]} | {row[3]}")
except ValueError:
    print("Geçersiz giriş. Lütfen bir sayı girin.")


conn.close()