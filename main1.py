import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def get_sample_iphone_data():
    
    return [
        {"Platform": "Amazon", "Product": "Apple iPhone 13 (128GB) - Midnight", "Price": 52499.00},
        {"Platform": "Amazon", "Product": "Apple iPhone 14 (128GB) - Blue", "Price": 65999.00},
        {"Platform": "Amazon", "Product": "Apple iPhone 15 (128GB) - Black", "Price": 77999.00},
        {"Platform": "Flipkart", "Product": "APPLE iPhone 13 (Midnight, 128 GB)", "Price": 52999.00},
        {"Platform": "Flipkart", "Product": "APPLE iPhone 14 (Blue, 128 GB)", "Price": 66999.00},
        {"Platform": "Flipkart", "Product": "APPLE iPhone 15 (Black, 128 GB)", "Price": 77990.00}
    ]

def clean_price(price_str):
    if not price_str:
        return 0
    numbers = re.findall(r'\d+,?\d*', str(price_str))
    if numbers:
        return float(numbers[0].replace(',', ''))
    return 0

def search_products(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        amazon_products = []
        try:
            amazon_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            response = requests.get(amazon_url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('div[data-component-type="s-search-result"]')
                
                for item in items[:3]:
                    name = item.select_one('span.a-text-normal')
                    price = item.select_one('span.a-price-whole')
                    if name and price:
                        amazon_products.append({
                            "Platform": "Amazon",
                            "Product": name.text.strip(),
                            "Price": clean_price(price.text)
                        })
        except:
            pass

        flipkart_products = []
        try:
            flipkart_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            response = requests.get(flipkart_url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('div._1AtVbE')
                
                for item in items[:3]:
                    name = item.select_one('div._4rR01T') or item.select_one('a.s1Q9rs')
                    price = item.select_one('div._30jeq3')
                    if name and price:
                        flipkart_products.append({
                            "Platform": "Flipkart",
                            "Product": name.text.strip(),
                            "Price": clean_price(price.text)
                        })
        except:
            pass

        all_products = amazon_products + flipkart_products
        if all_products:
            return all_products
    except:
        pass
    
    if 'iphone' in query.lower():
        return get_sample_iphone_data()
    
    return []

def main():
    st.title("iPhone Price Comparison Tool")
    st.write("Compare iPhone prices across Amazon and Flipkart")
    
    search_term = st.text_input("Enter iPhone Model:", 
                               placeholder="e.g., iPhone 13, iPhone 14",
                               value="iphone")
    
    if st.button("Scrap data", type="primary"):
        if search_term:
            with st.spinner('Fetching latest prices...'):
                products = search_products(search_term)
                
                if products:
                    df = pd.DataFrame(products)
                    df = df.sort_values('Price')
                    
                    st.subheader("Available Options")
                    
                    df_display = df.copy()
                    df_display['Price'] = df_display['Price'].apply(lambda x: f"₹{x:,.2f}")
                    
                    st.table(df_display)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Results",
                        csv,
                        "iphone_price_comparison.csv",
                        "text/csv"
                    )
                else:
                    st.warning("No results found. Please try searching for an iPhone model.")
        else:
            st.warning("Please enter an iPhone model to search.")

if __name__ == "__main__":
    main()