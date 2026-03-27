import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import requests
import argparse
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from urllib.parse import urljoin


def scrape_page(url):
    """Scrape all books from a single listing page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        books = soup.find_all("article", class_="product_pod")
        page_data = []
        
        for book in books:
            # Extract data from listing page
            title = book.h3.a["title"]
            
            # Clean price: remove weird encoding characters, keep only £ and digits/decimals
            raw_price = book.find("p", class_="price_color").text
            price = raw_price.encode('ascii', 'ignore').decode('ascii').strip()
            
            availability = book.find("p", class_="instock availability").text.strip()
            
            # Convert rating from string to number: "One"->1, "Two"->2, etc.
            rating_text = book.find("p")["class"][1].lower()
            rating_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            rating = rating_map.get(rating_text, 0)
            
            # Get product URL (relative path, need to make it absolute)
            product_rel_url = book.h3.a['href']
            # Fix: Add 'catalogue/' prefix if not present (for pages 2-5)
            if not product_rel_url.startswith('catalogue/'):
                product_rel_url = 'catalogue/' + product_rel_url
            product_url = urljoin("https://books.toscrape.com/", product_rel_url)
            
            # Scrape individual product page for additional details
            upc, description, num_reviews = scrape_product_page(product_url, headers)
            
            page_data.append({
                "Title": title,
                "Price": price,
                "Availability": availability,
                "Rating": rating,
                "Product_URL": product_url,
                "UPC": upc,
                "Description": description,
                "Number_of_Reviews": num_reviews
            })
            
        return page_data
        
    except requests.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return []

def scrape_product_page(product_url, headers):
    """Scrape individual product page for UPC, Description, and Reviews."""
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract UPC
        upc_elem = soup.find("th", string="UPC")
        upc = upc_elem.find_next_sibling("td").text.strip() if upc_elem else "N/A"
        
        # Extract Description
        desc_div = soup.find("div", id="product_description")
        if desc_div:
            desc_p = desc_div.find("p")
            description = desc_p.text.strip() if desc_p else "No description"
        else:
            description = "No description"
        
        # Extract Number of Reviews
        reviews_elem = soup.find("th", string="Number of reviews")
        num_reviews = reviews_elem.find_next_sibling("td").text if reviews_elem else "0"
        
        return upc, description, num_reviews
        
    except Exception as e:
        return "N/A", "No description", "0"

def main():
    """Main function with command-line argument support."""
    parser = argparse.ArgumentParser(
        description='Web scraper for books.toscrape.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Scrape 5 pages, save as books_data.xlsx
  %(prog)s -p 3               # Scrape 3 pages only
  %(prog)s -o my_data.csv     # Save as CSV with custom name
  %(prog)s -p 10 -o results.xlsx  # Scrape 10 pages, custom filename
        """
    )
    
    parser.add_argument('-p', '--pages', type=int, default=5,
                       help='Number of pages to scrape (default: 5)')
    parser.add_argument('-o', '--output', type=str, default='books_data.xlsx',
                       help='Output filename (default: books_data.xlsx). Supports .xlsx, .csv, .json')
    
    args = parser.parse_args()
    
    # Validate pages
    if args.pages < 1 or args.pages > 50:
        print("Error: Pages must be between 1 and 50")
        return
    
    # Determine file format from extension
    output_filename = args.output
    file_ext = os.path.splitext(output_filename)[1].lower()
    
    if file_ext not in ['.xlsx', '.csv', '.json']:
        print(f"Error: Unsupported file format '{file_ext}'. Use .xlsx, .csv, or .json")
        return
    
    all_data = []
    
    # Scrape pages 1 through N
    for page_num in range(1, args.pages + 1):
        if page_num == 1:
            url = "https://books.toscrape.com/"
        else:
            url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
        
        print(f"[INFO] Scraping page {page_num}/{args.pages}...")
        page_data = scrape_page(url)
        all_data.extend(page_data)
        
        # Add delay between pages (except after last page)
        if page_num < args.pages:
            time.sleep(1)
    
    # Save to file
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Create data directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.abspath(os.path.join(output_dir, output_filename))
        
        # Save based on file extension
        if file_ext == '.xlsx':
            df.to_excel(output_path, index=False)
        elif file_ext == '.csv':
            df.to_csv(output_path, index=False)
        elif file_ext == '.json':
            df.to_json(output_path, orient='records', indent=2)
        
        print(f"\n✅ Data saved to: {output_path}")
        print(f"📚 Total books scraped: {len(all_data)}")
        print(f"📊 Columns: {', '.join(df.columns.tolist())}")
        print("[SUCCESS] Scraping completed successfully! 🎉")
    else:
        print("No data was scraped!")

if __name__ == "__main__":
    main()