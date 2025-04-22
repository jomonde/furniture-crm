import sqlite3

def init_db():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()

    # Clients Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            rooms TEXT,
            style TEXT,
            budget TEXT
        )
    """)

    # Room Sketches Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS room_sketches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            room_type TEXT,
            dimensions TEXT,
            layout_notes TEXT,
            current_furniture TEXT,
            desired_furniture TEXT,
            special_considerations TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # Notes Table (new!)
    c.execute("""
        CREATE TABLE IF NOT EXISTS client_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            timestamp TEXT,
            type TEXT,  -- "AI", "Manual", "Follow-Up", etc.
            content TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    conn.commit()
    conn.close()

from datetime import datetime

def add_note(client_id, note_type, content):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO client_notes (client_id, timestamp, type, content) VALUES (?, ?, ?, ?)",
              (client_id, timestamp, note_type, content))
    conn.commit()
    conn.close()

def get_notes_by_client(client_id):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT id, timestamp, type, content FROM client_notes WHERE client_id = ? ORDER BY timestamp DESC", (client_id,))
    notes = c.fetchall()
    conn.close()
    return notes

def delete_note(note_id):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("DELETE FROM client_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def update_note(note_id, new_content):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("UPDATE client_notes SET content = ? WHERE id = ?", (new_content, note_id))
    conn.commit()
    conn.close()

def add_client(name, contact, rooms, style, budget):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("INSERT INTO clients (name, contact, rooms, style, budget) VALUES (?, ?, ?, ?, ?)",
              (name, contact, rooms, style, budget))
    conn.commit()
    conn.close()

def get_all_clients():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT name, contact, rooms, style, budget FROM clients")
    data = c.fetchall()
    conn.close()
    return data

def delete_client(name, contact):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE name = ? AND contact = ?", (name, contact))
    conn.commit()
    conn.close()

def update_client(original_name, original_contact, new_name, contact, rooms, style, budget):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("""
        UPDATE clients SET name = ?, contact = ?, rooms = ?, style = ?, budget = ?
        WHERE name = ? AND contact = ?
    """, (new_name, contact, rooms, style, budget, original_name, original_contact))
    conn.commit()
    conn.close()

def add_room_sketch(client_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO room_sketches (client_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations))
    conn.commit()
    conn.close()

def get_room_sketches_by_client(client_id):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("""
        SELECT room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations
        FROM room_sketches WHERE client_id = ?
    """, (client_id,))
    data = c.fetchall()
    conn.close()
    return data

def get_all_clients_with_ids():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT id, name, contact, rooms, style, budget FROM clients")
    data = c.fetchall()
    conn.close()
    return data

def update_client_notes(client_id, new_note, overwrite=False):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()

    if overwrite:
        updated_notes = new_note
    else:
        # Append mode
        c.execute("SELECT notes FROM clients WHERE id = ?", (client_id,))
        current = c.fetchone()
        current_notes = current[0] if current and current[0] else ""
        updated_notes = current_notes + "\n\n" + new_note

    c.execute("UPDATE clients SET notes = ? WHERE id = ?", (updated_notes, client_id))
    conn.commit()
    conn.close()
