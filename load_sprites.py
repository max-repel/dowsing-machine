import base64
import os
import re
import duckdb

conn = duckdb.connect("dowsing-machine.duckdb")

conn.execute("""
DROP TABLE IF EXISTS sprites
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS sprites (
    sprite_id INTEGER,
    sprite_name TEXT,
    sprite_data TEXT
)
""")


folder = "./pokesprites"

first_base64 = None


for filename in os.listdir(folder):
    if filename.endswith(".png") and filename[:-4].isdigit() and filename != "0.png":
        match = re.fullmatch(r"(\d+)\.png", filename)
        sprite_id = int(match.group(1))
        path = os.path.join(folder, filename)

        with open(path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")

            full_uri = f"data:image/png;base64,{base64_string}"

            if first_base64 is None:
                first_base64 = full_uri

        conn.execute(
            "INSERT INTO sprites (sprite_id, sprite_name, sprite_data) VALUES (?, ?, ?)",
            (sprite_id, filename, full_uri)
        )

conn.commit()


tables = conn.execute("SHOW TABLES").fetchall()
print(tables)

print(first_base64)
