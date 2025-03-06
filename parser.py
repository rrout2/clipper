import pandas as pd
import pdfplumber
import argparse

def fastpass_info(df):
    count_fastpass = df[(df["PRODUCT"] == "SF Muni Adult Fastpass") & (df["CREDIT"] == "")].shape[0]
    if count_fastpass == 0:
        print("No SF Muni Fastpass used.")
        return

    num_bart_sf_rides = df[(df["TRANSACTION TYPE"] == "Dual-tag exit transaction, fare payment") & 
            (df["PRODUCT"] == "SF Muni Adult Fastpass")].shape[0]
    print(f"Number of BART rides taken with SF Muni Fastpass: {num_bart_sf_rides}")

    count_sfm_bus = df[df["LOCATION"] == "SFM bus"].shape[0]
    print(f"Total taps on Muni: {count_sfm_bus}")

    df_bus = df[df["LOCATION"] == "SFM bus"].copy()
    df_bus["DATE"] = pd.to_datetime(df_bus["DATE"], format='%m-%d-%Y %I:%M %p')

    seen_times = set()
    num_transfers = 0
    for _, row in df_bus.iterrows():
        time = row["DATE"]
        if any(abs((time - seen_time).total_seconds()) <= 7200 for seen_time in seen_times):
            num_transfers += 1
            continue
        seen_times.add(time)
    num_bus_rides = len(seen_times)

    print(f"Number of 2 hr Muni rides taken: {num_bus_rides}")
    print(f"Number of transfers: {num_transfers}")
    print(f"Total cost without pass =\n{num_bus_rides} * $2.75 + {num_bart_sf_rides} * $2.40 = ${num_bus_rides * 2.75 + num_bart_sf_rides * 2.4}")

def is_fastpass_worth_it(df):
    sf_bart_stops = {
        "Balboa Park",
        "Glen Park",
        "24th St Mission",
        "16th St Mission",
        "Civic Center (BART)",
        "Powell St (BART)",
        "Montgomery (BART)",
        "Embarcadero (BART)",
    }
    num_muni_rides = df[(df["LOCATION"] == "SFM bus") & (df["DEBIT"] != "")].shape[0]
    num_bart_rides = df[(df["LOCATION"].isin(sf_bart_stops)) & \
                        (df["TRANSACTION TYPE"] == "Dual-tag exit transaction, fare payment") & \
                            (df["LOCATION"].shift(1).isin(sf_bart_stops))].shape[0]
    muni_cost = num_muni_rides * 2.75
    total_cost = muni_cost + num_bart_rides * 2.4
    fastpass_m_cost = 85
    fastpass_a_cost = 102
    not_worth_m = muni_cost < fastpass_m_cost
    not_worth_a = total_cost < fastpass_a_cost
    
    print(f"Number of Muni rides: {num_muni_rides}")
    print(f"Number of BART rides: {num_bart_rides}")
    print(f"Muni cost =\n{num_muni_rides} * $2.75 = ${muni_cost}")
    print(f"Total cost =\n{num_muni_rides} * $2.75 + {num_bart_rides} * $2.40 = ${total_cost}\n")
    print(f"Muni-only Fastpass (${fastpass_m_cost}) would {'not ' if not_worth_m else ''}have been worth it.")
    print(f"Muni+BART Fastpass (${fastpass_a_cost}) would {'not ' if not_worth_a else ''}have been worth it.")


def parse_pdf(pdf_path):
    df = pd.DataFrame(columns=["DATE", "TRANSACTION TYPE", "LOCATION", "ROUTE", "PRODUCT", "DEBIT", "CREDIT", "BALANCE"])
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
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
    return df

def main():
    parser = argparse.ArgumentParser(description='Convert Clipper Card ride history PDF to CSV')
    parser.add_argument('pdf_path', help='Path to the Clipper Card transaction history PDF')
    parser.add_argument('-o', '--output', help='Output CSV file', default='clipper_transactions.csv')
    parser.add_argument('-fp', '--fastpass', help='Whether to print fastpass info', default='false')
    parser.add_argument('-w', '--worthit', help='Whether to check if fastpass would have been worth it', default='false')
    
    args = parser.parse_args()

    df = parse_pdf(args.pdf_path)
    
    df.to_csv(args.output, index=False)

    if args.fastpass[0].lower() == 't':
        fastpass_info(df)

    if args.worthit[0].lower() == 't':
        is_fastpass_worth_it(df)

if __name__ == "__main__":
    main()
