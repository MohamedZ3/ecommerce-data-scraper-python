# 📚 Books to Scrape - Web Scraping Demo

A professional, production-ready web scraper for extracting book data from [books.toscrape.com](https://books.toscrape.com). Perfect for learning web scraping or as a foundation for client projects.

---

## 🚀 Quick Start (For Clients)

### Installation

```bash
# Install Python 3.9+ if you don't have it
# Then install dependencies:
pip3 install -r requirements.txt
```

### Basic Usage

```bash
# Scrape 5 pages (default) and save as Excel
python3 src/scraper.py

# Scrape only 3 pages
python3 src/scraper.py -p 3

# Save as CSV with custom name
python3 src/scraper.py -o my_books.csv

# Scrape 10 pages and save as JSON
python3 src/scraper.py -p 10 -o results.json
```

### Output

All scraped data is saved in the `data/` folder with these columns:

- **Title** - Book title
- **Price** - Price in GBP (cleaned format)
- **Availability** - Stock status
- **Rating** - Star rating (1-5)
- **Product_URL** - Link to product page
- **UPC** - Universal Product Code
- **Description** - Book description
- **Number_of_Reviews** - Review count

---

## ⚙️ Command-Line Options

| Option         | Description                      | Default           | Example          |
| -------------- | -------------------------------- | ----------------- | ---------------- |
| `-p, --pages`  | Number of pages to scrape (1-50) | 5                 | `-p 10`          |
| `-o, --output` | Output filename with extension   | `books_data.xlsx` | `-o my_data.csv` |

**Supported formats:** `.xlsx` (Excel), `.csv`, `.json`

---

## 🛠️ For Developers

### How It Works

```
1. Fetch listing page HTML
   ↓
2. Parse with BeautifulSoup
   ↓
3. Find all book containers (<article class="product_pod">)
   ↓
4. For each book:
   - Extract: title, price, availability, rating
   - Build product URL (handles relative paths)
   - Fetch individual product page
   - Extract: UPC, description, reviews
   ↓
5. Collect all data into list of dictionaries
   ↓
6. Convert to Pandas DataFrame
   ↓
7. Save to file (Excel/CSV/JSON)
```

### Key Technical Details

**URL Construction Fix:**
The website uses different URL patterns for product links on page 1 vs pages 2+. The code automatically detects and adds the `catalogue/` prefix when needed:

```python
if not product_rel_url.startswith('catalogue/'):
    product_rel_url = 'catalogue/' + product_rel_url
```

**Data Cleaning:**

- **Price**: Removes encoding artifacts (`Â£` → `£`)
- **Rating**: Converts text ("One", "Two") to integers (1, 2, 3, 4, 5)

**Error Handling:**

- Network errors are caught and logged
- Missing data fields default to "N/A" or "0"
- Individual product failures don't stop the entire scrape

### Project Structure

```
.
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── src/
│   └── scraper.py       # Main scraper code
├── data/                 # Output directory (gitignored)
│   ├── books_data.xlsx  # Example output
│   ├── *.csv           # Other outputs
│   └── *.json          # Other outputs
└── .gitignore           # Excludes data/ and cache
```

### Code Architecture

**Functions:**

| Function                                    | Purpose                                                |
| ------------------------------------------- | ------------------------------------------------------ |
| `scrape_page(url)`                          | Scrape one listing page, return list of book data      |
| `scrape_product_page(product_url, headers)` | Scrape individual product page for extra details       |
| `main()`                                    | Orchestrate pagination, collect all data, save to file |

**Data Flow:**

- `scrape_page()` → returns `list[dict]` with 8 fields per book
- `main()` → extends `all_data` with each page's results
- Pandas DataFrame → exported to chosen format

---

## 📦 Dependencies

| Package          | Version | Purpose                    |
| ---------------- | ------- | -------------------------- |
| `beautifulsoup4` | 4.12.3  | HTML parsing               |
| `pandas`         | 2.2.1   | Data manipulation & export |
| `requests`       | 2.31.0  | HTTP requests              |
| `lxml`           | 5.1.0   | Fast XML/HTML parser       |

Install all: `pip3 install -r requirements.txt`

---

## 🎯 Use Cases

✅ **Learning web scraping** - Clean, well-commented code  
✅ **Freelance portfolio** - Professional structure & error handling  
✅ **Data collection** - Export to Excel/CSV/JSON  
✅ **Template project** - Adapt for other websites by changing selectors

---

## 🔧 Customization Guide

### To Scrape a Different Website:

1. Update the base URL in `main()`:

   ```python
   url = f"https://your-target-site.com/page-{page_num}.html"
   ```

2. Inspect the website's HTML (Right-click → Inspect)
   - Find the container element for items (e.g., `<div class="product">`)
   - Update `soup.find_all("article", class_="product_pod")` (line 19)
   - Find selectors for title, price, etc. and update lines 24-27

3. Adjust product page selectors in `scrape_product_page()` (lines 63-77)

4. Modify pagination logic if needed (lines 88-93)

---

## ⚠️ Important Notes

- **Respect robots.txt**: This demo site allows scraping. Always check `robots.txt` for production sites.
- **Rate limiting**: Add `time.sleep(1)` between requests to be polite.
- **Legal compliance**: Ensure you have permission to scrape target websites.
- **User-Agent**: The scraper includes a User-Agent header to mimic a real browser.

---

## 🐛 Troubleshooting

**"ModuleNotFoundError"**

```bash
pip3 install -r requirements.txt
```

**"zsh: command not found: python3"**

```bash
# Use 'python' instead, or install Python 3
python -m pip install -r requirements.txt
```

**No data in output file**

- Check internet connection
- Verify the target website is accessible
- Look for error messages in terminal output

**Encoding issues in price**
The code already handles this with ASCII cleaning. If issues persist, check the website's charset.

---

## 📄 License

This is a demo project for educational purposes. Adapt as needed for your use case.

---

## 🙋 Support

For issues or questions:

1. Check the code comments in `src/scraper.py`
2. Review BeautifulSoup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
3. Inspect website HTML structure using browser DevTools

---

**Happy Scraping! 🎉**
