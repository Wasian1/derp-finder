import os
import re
from playwright.sync_api import sync_playwright
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv() 

def clean_and_parse_price(price_str: str) -> float:
    """Extracts the first floating point number from a messy price string."""
    if not price_str or "Free" in price_str or "Included" in price_str:
        return 0.0
    match = re.search(r"[-+]?\d*\.\d+|\d+", price_str.replace(",", ""))
    return float(match.group()) if match else 0.0

def send_summary_email(summary_df: pd.DataFrame):
    """Converts a Pandas DataFrame to a styled HTML table and sends it via SMTP."""
    # --- CONFIGURATION INITIALIZATION ---
    # Replace these strings with your actual email credentials
    sender_email = "derp.finder.inc@gmail.com"
    sender_password =  os.environ.get("EMAIL_APP_PASSWORD")  # Use a Google App Password if using Gmail
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "dcfitzsimmons1995@gmail.com")
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    print("\n📬 Preparing to dispatch email alert summary...")
    
    # Construct standard email boundaries
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "TCGplayer Automated Scraping Alert Summary"

    # Convert the Pandas DataFrame into a clean HTML table structure
    # We remove the index column and add a custom CSS class name for styling
    html_table = summary_df.to_html(index=False, classes="tcg-data-table")

    # 2. Build out the styled HTML template wrapper
    email_html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333333;
                line-height: 1.6;
            }}
            .tcg-data-table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 15px;
                font-size: 13px;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            }}
            .tcg-data-table th {{
                background-color: #007bff;
                color: white;
                text-align: left;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #dddddd;
            }}
            .tcg-data-table td {{
                padding: 10px;
                border: 1px solid #dddddd;
            }}
            /* Zebra striping for easy reading */
            .tcg-data-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            /* Dynamic row coloring depending on target value string metrics */
            td:last-child {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <p>Hello hooman,</p>
        <p>Your scheduled TCGplayer card scraping automation run has successfully completed. <br>
        Below is the styled summary report showcasing the cheapest tracked marketplace options:</p>
        
        {html_table}
        
        <br>
        <p>Best regards,<br>
        Derp Finder Inc.</p>
    </body>
    </html>
    """

    # 3. Attach the payload as "html" instead of "plain" text strings
    msg.attach(MIMEText(email_html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("✅ HTML Email summary notification dispatched successfully!")
    except Exception as e:
        print(f"❌ Failed to dispatch email automated alerts: {e}")
    finally:
        server.quit()

def scrape_single_card(page, base_url: str, max_items_per_card: int, budget_target: float) -> list:
    """Scrapes snapshot stats and page numbers iteratively for a single card URL."""
    card_records = []
    current_page = 1
    card_name = "Unknown Card"
    
    # Placeholder metadata metrics
    low_price, high_price, total_sold = "Unknown", "Unknown", "Unknown"
    timeframe_label = "3 Month Snapshot"  # Default initial state flag

    print(f"  -> Initializing page state for market history snapshot capture...")
    page.goto(f"{base_url}?page=1", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)  # static buffer wait
    
    # Grab the official Card Name cleanly from the main H1 header
    name_selector = "h1.product-details__name, h1.product-name, h1"
    if page.locator(name_selector).count() > 0:
        card_name = page.locator(name_selector).first.inner_text().strip()
        print(f"  [Identified Card Name]: {card_name}")

    # --- ADVANCED INTERACTION: FORCE CLICK 1Y VIA JAVASCRIPT INJECTION ---
    try:
        # Use evaluate to find the '1Y' or '1 Year' tab option inside the page engine context
        clicked_successfully = page.evaluate("""() => {
            const elements = Array.from(document.querySelectorAll('button, span, li, a, div'));
            const target = elements.find(el => {
                const txt = el.textContent.trim();
                return txt === '1Y' || txt === '1 Year' || txt === '1Y ';
            });
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""")
        
        if clicked_successfully:
            print("  [Action] Programmatically selected 1Y timeframe via JS injection.")
            page.wait_for_timeout(2000)  # Pause for text transition transformations
            timeframe_label = "1 Year Snapshot"
        else:
            print("  [Warning] 1Y toggle not found via JS. Relying on default layout views.")
        
        # Scroll down slightly to make sure layout components paint fully
        page.evaluate("window.scrollTo(0, 400);")
        page.wait_for_timeout(500)
        body_text = page.locator("body").inner_text()

        # Flexible regex scanning document text maps
        low_match = re.search(r"Low\s*Sale\s*Price:?\s*(\$[0-9.,]+)", body_text, re.IGNORECASE)
        high_match = re.search(r"High\s*Sale\s*Price:?\s*(\$[0-9.,]+)", body_text, re.IGNORECASE)
        sold_match = re.search(r"Total\s*Sold:?\s*([0-9,]+)", body_text, re.IGNORECASE)
        
        if low_match: low_price = low_match.group(1).strip()
        if high_match: high_price = high_match.group(1).strip()
        if sold_match: total_sold = sold_match.group(1).strip()
        
        # Double check document logs to catch true active state layout text strings
        if "1 Year Snapshot" in body_text:
            timeframe_label = "1 Year Snapshot"
        elif "3 Month Snapshot" in body_text and not clicked_successfully:
            timeframe_label = "3 Month Snapshot"

        print(f"  [{timeframe_label} Metrics] Low: {low_price} | High: {high_price} | Total Sold: {total_sold}")
        
    except Exception as e:
        print(f"  Non-blocking error reading chart snapshot metrics: {e}")

    # --- STEP 2: LOOP THROUGH PAGINATION FOR SELLER LISTINGS ---
    while len(card_records) < max_items_per_card:
        target_url = f"{base_url}?page={current_page}"
        print(f"  -> Scraping Page {current_page} | Total items found for this card: {len(card_records)}")
        
        if current_page > 1:
            page.wait_for_timeout(1000)  # Pacing delay to simulate human browsing behavior
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        
        page.evaluate("window.scrollTo(0, 1200);")
        page.wait_for_timeout(1500)
        
        listing_selector = "div.listing-item, .listing-item"
        if page.locator(listing_selector).count() == 0:
            print("  No visible listings located on this pagination screen. Ending card loop.")
            break
            
        listings = page.locator(listing_selector)
        for i in range(listings.count()):
            item = listings.nth(i)
            
            price_element = item.locator(".listing-item__listing-data__info__price")
            shipping_element = item.locator(".listing-item__listing-data__info__shipping-message")
            seller_element = item.locator(".seller-info__name") 
            condition_element = item.locator(".listing-item__product-condition, .product-condition, h3, .listing-item__listing-data__info")
            
            if price_element.count() > 0 and price_element.inner_text().strip():
                raw_price = price_element.inner_text().strip()
                raw_shipping = shipping_element.inner_text().strip() if shipping_element.count() > 0 and shipping_element.inner_text().strip() else "Free Shipping"
                seller = seller_element.inner_text().strip() if seller_element.count() > 0 else "Unknown"
                
                condition = "Unknown"
                if condition_element.count() > 0:
                    raw_text = condition_element.first.inner_text().strip()
                    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
                    valid_conditions = ["Near Mint", "Lightly Played", "Moderately Played", "Heavily Played", "Damaged"]
                    for line in lines:
                        if any(cond in line for cond in valid_conditions):
                            condition = line
                            break
                
                card_records.append({
                    "Card Name": card_name,
                    "Max Willing To Pay": f"${budget_target:.2f}" if budget_target > 0 else "No Limit",
                    "Timeframe Tracking": timeframe_label,
                    "Market Low Sale": low_price,   
                    "Market High Sale": high_price,
                    "Market Total Sold": total_sold,
                    "Seller": seller,
                    "Condition": condition,
                    "Price": raw_price,
                    "Shipping": raw_shipping
                })
                
        current_page += 1
        if current_page > 10:
            break
            
    return card_records

def main():
    print("🚀 Script execution started...")
    
    # 1. Automatically calculate the absolute path to src/scrape_list/card_list.txt
    current_script_dir = os.path.dirname(os.path.abspath(__file__)) # src/scraper/
    project_root = os.path.dirname(current_script_dir) # src/

    max_items_per_card = 70  # Limit to avoid excessive scraping per card

    target_csv_name = os.environ.get("TARGET_CSV_NAME", "card_list.csv")  # Default to card_list.csv if not set
    
    
    # 1. Look for the newly generated .csv list instead of plain .txt
    input_csv = os.path.join(project_root, "scrape_list", target_csv_name)
    output_path = os.path.join(os.path.dirname(project_root), "data",f"output_{target_csv_name}")
    
    if not os.path.exists(input_csv):
        print(f"❌ Error: Config file not found at path: {input_csv}")
        return

    # 2. Read spreadsheet configurations securely using Pandas dataframes
    input_df = pd.read_csv(input_csv)
    if input_df.empty or "url" not in input_df.columns:
        print("❌ Error: Input CSV matrix formatting error or file contains no data rows.")
        return
        
    print(f"📋 Loaded {len(input_df)} tracked card targets from tracking configuration file.")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    master_records_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

         # --- NEW OPTIMIZATION: BLOCK IMAGES & CSS ASSETS TO ACCELERATE CLOUD LOAD ---
        def block_media_and_analytics(route):
            if route.request.resource_type in ["image", "font", "stylesheet", "media"] or "analytics" in route.request.url:
                route.abort()
            else:route.continue_()
            page.route("**/*", block_media_and_analytics)
        
        try:
            for idx, row in input_df.iterrows():
                url = str(row["url"]).strip()
                max_willing_to_pay = float(row["max_price"]) if "max_price" in input_df.columns and pd.notna(row["max_price"]) else 0.0
                print(f"\n==================================================")
                print(f"Processing URL [{idx}/{len(input_df)}]: {url}")
                print(f"Target Budget Threshold: ${max_willing_to_pay:.2f}" if max_willing_to_pay > 0 else "Target Budget Threshold: None")
                print(f"==================================================")
                
                card_data = scrape_single_card(page, url, max_items_per_card, max_willing_to_pay)
                master_records_list.extend(card_data)
                
            df = pd.DataFrame(master_records_list).drop_duplicates(subset=["Card Name", "Seller", "Price"])
            
            if not df.empty:
                print(f"\nTotal marketplace rows compiled globally: {len(df)}")
                
                price_floats = df["Price"].apply(clean_and_parse_price)
                shipping_floats = df["Shipping"].apply(clean_and_parse_price)
                total_floats = price_floats + shipping_floats
                
                df["Total Cost"] = total_floats.apply(lambda x: f"${x:.2f}")
                df["_raw_total"] = total_floats
                
                df = df.sort_values(by=["Card Name", "_raw_total"], ascending=[True, True]).drop(columns=["_raw_total"])
                
                allowed_conditions = ["Near Mint", "Lightly Played"]
                filtered_df = df[df["Condition"].str.contains('|'.join(allowed_conditions), case=False, na=False)]

                raw_budgets = filtered_df["Max Willing To Pay"].apply(lambda x: clean_and_parse_price(x))
                raw_totals = filtered_df["Total Cost"].apply(lambda x: clean_and_parse_price(x))

                # --- EXPLICIT STRING CONVERSION: MAP TRUE/FALSE TO YES/NO ---
                is_within_budget = (raw_totals <= raw_budgets) | (raw_budgets == 0.0)
                filtered_df["Within Budget"] = is_within_budget.map({True: "YES", False: "NO"})

                filtered_df.to_csv(output_path, index=False)
                print(f"\nProcessing Run Successful! Saved filtered card data combinations into {output_path}")
                
                # Group and isolate the absolute cheapest matching row per card variant
                summary_preview = filtered_df.groupby("Card Name").first().reset_index()

                # Target columns list cleanly arranged for your text printouts
                target_columns = ["Card Name", "Seller", "Condition", "Timeframe Tracking", "Market Low Sale", "Market High Sale", "Total Cost", "Max Willing To Pay", "Within Budget"]
                summary_final_df = summary_preview[target_columns]

                # Print plain text summary table to local terminal session
                print("\nTop cheapest deal found for each processed card variant:")
                print(summary_final_df.to_string(index=False))

                # --- EXPLICIT DATA CONVERSION CHANGE ---
                # # Pass the raw DataFrame slice into the email dispatcher instead of a text string
                send_summary_email(summary_final_df)
            else:
                print("No data extracted across the configuration tracking runs.")

        except Exception as e:
            print(f"Global master engine processing error: {e}")
        finally:
            context.close()

if __name__ == "__main__":
    main()