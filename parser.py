import pandas as pd
import pdfplumber
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Clipper Card ride history PDF to CSV')
    parser.add_argument('pdf_path', help='Path to the Clipper Card transaction history PDF')
    parser.add_argument('-o', '--output', help='Output CSV file', default='clipper_transactions.csv')
    args = parser.parse_args()

    df = pd.DataFrame(columns=["DATE", "TRANSACTION TYPE", "LOCATION", "ROUTE", "PRODUCT", "DEBIT", "CREDIT", "BALANCE"])
    try:
        with pdfplumber.open(args.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                x0_date = page.search("TRANSACTION DATE")[0].get("x0")
                x0_type = page.search("TRANSACTION TYPE")[0].get("x0")
                x0_location = page.search("LOCATION")[0].get("x0")
                x0_route = page.search("ROUTE")[0].get("x0")
                x0_product = page.search("PRODUCT")[0].get("x0")
                x0_debit = page.search("DEBIT")[0].get("x0")
                x0_credit = page.search("CREDIT")[0].get("x0")
                x0_balance = page.search("BALANCE")[0].get("x0")

                bottom_bound = page.search("Note: If there is a discrepancy")[0].get("top")
                page = page.crop((0, 0, page.width, bottom_bound + 10))

                table = page.extract_table({
                    "vertical_strategy": "explicit", 
                    "explicit_vertical_lines": [x0_date, x0_type, x0_location, x0_route, x0_product, x0_debit, x0_credit, x0_balance, 800],
                    "explicit_horizontal_lines": [bottom_bound]
                })
                for row in table:
                    if row[0] == "TRANSACTION DATE" or row[0] == '':
                        continue
                    df.loc[len(df)] = row
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    df.to_csv(args.output, index=False)
