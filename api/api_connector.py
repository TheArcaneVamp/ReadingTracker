import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def get_cover(cover_url):
    
    if not cover_url:
        return None
    
    try:
        response = requests.get(cover_url)
        response.raise_for_status()
        
        return response.content
    
    except requests.exceptions.RequestException as e:    
        print(f"Exception Occurred:{e}")
        return None

def get_description(b_id):
    url = f"https://openlibrary.org/works/{b_id}.json"
    
    try:
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        desc = data.get("description", "No Description Available")
        if type(desc) is dict:
            return desc.get("value", "No Description Available")
        elif type(desc) is str:
            return desc
        else:
            return "No Description Available"
        
    except requests.exceptions.RequestException as e:
        
        print(f"Exception Occurred: {e}")
        return "No Description Found"

        
    

def get_book(name):
    
    params = {
        "q": name,
        "fields": "key,title,author_name,first_publish_year,cover_i",
        "limit": 5
    }

    try:
        response = requests.get(OPEN_LIBRARY_URL, params)
        print(f"Response Status Code:{response.status_code}")
        #print(f"Response Content:\n{response.content}")

        data = response.json()

        if data['numFound']==0:
            print("No Books Found!")
            return []
        
        books_found = data['docs']

        parsed_books = []

        for index, book in enumerate(books_found, start=1):
            title = book.get("title", "Unknown Title")
            author = book.get("author_name", ["Unknown Author"])
            year_published = book.get("first_publish_year", "Unknown Year")
            cover_id = book.get("cover_i")
            b_id = book.get("key").split('/')[2]
            if cover_id:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            else:
                cover_url = None

            book_entry = {
                "b_id":b_id,
                "title":title,
                "author":author,
                "year_published":year_published,
                "cover_url":cover_url
            }

            parsed_books.append({"index":index, "book_entry":book_entry})

        return parsed_books
    
    except requests.exceptions.RequestException as e:
        
        print(f"Exception Occurred: {e}")
        return []



if __name__ == "__main__":
    res = get_book("The Lord of The Rings")
    print(res)
    print(get_description(res[0]['book_entry']['b_id']))