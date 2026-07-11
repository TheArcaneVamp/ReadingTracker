import sqlite3

def create_db():
    con = sqlite3.connect("reading_tracker.db")
    cursor = con.cursor()

    queries_list = [
        """
            CREATE TABLE IF NOT EXISTS Books
            (
            	b_id TEXT PRIMARY KEY,
            	title TEXT NOT NULL,
            	year_published DATE,
            	status TEXT CHECK (status IN ('Finished', 'TBR', 'DNF', 'CR')),
            	rating INTEGER CHECK (rating >= 1 AND rating <= 10),
            	cover_url TEXT,
            	description TEXT,
            	start_date DATE,
            	finish_date DATE
            );          
        """,
        """
            CREATE TABLE IF NOT EXISTS Authors
            (
	            a_id INTEGER PRIMARY KEY AUTOINCREMENT,
	            author_name TEXT UNIQUE NOT NULL	
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS Written_By
            (
            	b_id TEXT REFERENCES Books(b_id) ON DELETE CASCADE,
            	a_id INTEGER REFERENCES Authors(a_id) ON DELETE CASCADE,
            	PRIMARY KEY(b_id, a_id)
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS Genre
            (
            	g_id INTEGER PRIMARY KEY AUTOINCREMENT,
            	genre_name TEXT UNIQUE NOT NULL
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS Books_Genre
            (
            	b_id TEXT REFERENCES Books(b_id) ON DELETE CASCADE,
            	g_id INTEGER REFERENCES Genre(g_id) ON DELETE CASCADE,
            	PRIMARY KEY(b_id, g_id)
            );
        """
    ]

    try:
        
        cursor.execute("PRAGMA foreign_keys = ON;")

        for query in queries_list:
            cursor.execute(query)

        print("Database Schema Created")
        con.commit()

    except  sqlite3.OperationalError as e:
        
        print(f"Databse Creation Failed: {e}")
    
    finally:
        con.close()

if __name__ == "__main__":
    create_db()