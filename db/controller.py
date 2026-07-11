import sqlite3
import api.api_connector as api

DB_PATH = "reading_tracker.db"

def insert_book(book):
    b_id = book['b_id']
    title = book['title']
    authors = book['author']
    year_published = book['year_published']
    cover_url = book['cover_url']
    description = api.get_description(b_id)
    
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        insert_query = """
        INSERT INTO BOOKS(b_id, title, year_published, status, rating, cover_url, description, start_date, finish_date)
        VALUES(?, ?, ?, 'TBR', NULL, ?, ?, NULL, NULL)"""
        cursor.execute(insert_query, (b_id, title, year_published, cover_url, description))
        
        for author in authors:
            cursor.execute("INSERT OR IGNORE INTO Authors(author_name) VALUES(?)", (author,))
            cursor.execute("SELECT a_id FROM Authors WHERE author_name = ?", (author,))
            a_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO Written_By(b_id, a_id) VALUES(?,?)", (b_id, a_id))
        
        con.commit()
        
        return True, f"{title} inserted into your Library!"
    
    except sqlite3.IntegrityError as e:
        
        return False, f"Integrity Error occurred: {e}"
    
    except Exception as e:
        
        return False, f"Some Error occurred: {e}"
    
    finally:
        if 'con' in locals() and con:
            con.close()
            
def fetch_all_books():
    
    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        
        cursor.execute("SELECT b_id, title, cover_url, status FROM Books")
        return [dict(row) for row in cursor.fetchall()]
    
    except Exception as e:
        
        print(f"An Error Occurred: {e}")
        return []
        
    finally:
        
        if 'con' in locals() and con:
            con.close()
            
def fetch_book_details(b_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get core book info
        cursor.execute("SELECT * FROM Books WHERE b_id = ?", (b_id,))
        book = dict(cursor.fetchone())
        
        # Join junction table to get authors
        cursor.execute("""
            SELECT a.author_name FROM Authors a
            JOIN Written_By wb ON a.a_id = wb.a_id
            WHERE wb.b_id = ?
        """, (b_id,))
        authors = [row['author_name'] for row in cursor.fetchall()]
        book['author_string'] = ", ".join(authors)
        
        return book
    except Exception as e:
        print(f"Fetch details error: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        
def update_book_status(b_id, status, rating):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # If rating is 0, we convert it to NULL in the database
        db_rating = rating if rating > 0 else None
        
        cursor.execute("""
            UPDATE Books 
            SET status = ?, rating = ?
            WHERE b_id = ?
        """, (status, db_rating, b_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()       
        
def fetch_filtered_books(search_text="", status="All", author="", year="", rating="All"):
    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        
        query = "SELECT b_id, title, cover_url, status FROM Books WHERE 1=1"
        params = []
        
        # 1. Filter by Title
        if search_text:
            query += " AND title LIKE ?"
            params.append(f"%{search_text}%")
            
        # 2. Filter by Status
        if status != "All":
            query += " AND status = ?"
            params.append(status)
            
        # 3. Filter by Author (Subquery)
        if author:
            query += """ AND b_id IN (
                SELECT wb.b_id FROM Written_By wb
                JOIN Authors a ON wb.a_id = a.a_id
                WHERE a.author_name LIKE ?
            )"""
            params.append(f"%{author}%")
            
        # 4. Filter by Year
        if year:
            query += " AND year_published = ?"
            params.append(year)
            
        # 5. Filter by Rating
        if rating != "All":
            query += " AND rating = ?"
            params.append(rating)
            
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Filter error: {e}")
        return []
    finally:
        if 'con' in locals() and con:
            con.close()