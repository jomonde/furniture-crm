import sqlite3

conn = sqlite3.connect("clients.db")
c = conn.cursor()

print("\nAll Clients With Notes:\n")
for row in c.execute("SELECT id, name, contact, notes FROM clients"):
    print(f"ID: {row[0]} | Name: {row[1]} | Contact: {row[2]}")
    print("Notes:")
    print(row[3] or "(None)")
    print("-" * 40)

# TEST WRITE: Update notes manually
c.execute("UPDATE clients SET notes = ? WHERE id = ?", ("Test note here", 1))
conn.commit()

conn.close()

