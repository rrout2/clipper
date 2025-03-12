import pandas as pd
import pdfplumber
import argparse

# Column names
DATE = "DATE"
TRANSACTION_TYPE = "TRANSACTION_TYPE"
LOCATION = "LOCATION"
ROUTE = "ROUTE"
PRODUCT = "PRODUCT"
DEBIT = "DEBIT"
CREDIT = "CREDIT"
BALANCE = "BALANCE"

# Constants
MUNI_BUS = "SFM bus"
FASTPASS_A = "SF Muni Adult Fastpass"
EXIT_TAG = "Dual-tag exit transaction, fare payment"
SF_BART_STOPS = {
    "Balboa Park",
    "Glen Park",
    "24th St Mission",
    "16th St Mission",
    "Civic Center (BART)",
    "Powell St (BART)",
    "Montgomery (BART)",
    "Embarcadero (BART)",
}

MUNI_METRO_STATIONS_REGEX = '(?i)(Van Ness|Church|Castro|Forest Hill|West Portal|\(Muni\))'

def is_muni(df):
    return (df[LOCATION] == MUNI_BUS) | (df[LOCATION].str.contains(MUNI_METRO_STATIONS_REGEX, regex=True))

def is_bart_exit(df):
    return df[TRANSACTION_TYPE] == EXIT_TAG

def is_bart_exit_within_sf(df):
    return is_bart_exit(df) & (df[LOCATION].isin(SF_BART_STOPS) & (df[LOCATION].shift(1).isin(SF_BART_STOPS)))

def is_fastpass(df):
    return (df[PRODUCT] == FASTPASS_A)

def fastpass_info(df):
    count_fastpass = df[is_fastpass(df) & (df[CREDIT] == "")].shape[0]
    if count_fastpass == 0:
        print("No SF Muni Fastpass used.")
        return {}

    num_bart_sf_rides = df[is_bart_exit(df) & is_fastpass(df)].shape[0]

    total_muni_taps = df[is_muni(df)].shape[0]

    df_muni = df[is_muni(df)].copy()
    df_muni[DATE] = pd.to_datetime(df_muni[DATE], format='%m-%d-%Y %I:%M %p')

    seen_times = set()
    num_transfers = 0
    for _, row in df_muni.iterrows():
        time = row[DATE]
        if any(abs((time - seen_time).total_seconds()) <= 7200 for seen_time in seen_times):
            num_transfers += 1
            continue
        seen_times.add(time)
    num_bus_rides = len(seen_times)

    print(f"Number of BART rides: {num_bart_sf_rides}")
    print(f"Total taps on Muni: {total_muni_taps}")
    print(f"Number of 2 hr Muni rides taken: {num_bus_rides}")
    print(f"Number of transfers: {num_transfers}")
    print(f"Total cost without pass =\n{num_bus_rides} * $2.75 + {num_bart_sf_rides} * $2.40 = ${num_bus_rides * 2.75 + num_bart_sf_rides * 2.4}")

    results = {}
    results["muni_rides_taken"] = num_bus_rides
    results["bart_rides_taken"] = num_bart_sf_rides
    results["transfers"] = num_transfers
    results["cost_without_pass"] = num_bus_rides * 2.75 + num_bart_sf_rides * 2.4
    
    return results

def is_fastpass_worth_it(df):
    num_muni_rides = df[is_muni(df) & (df[DEBIT] != "")].shape[0]
    num_bart_rides = df[is_bart_exit_within_sf(df)].shape[0]
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

    results = {}
    results["muni_rides_taken"] = num_muni_rides
    results["bart_rides_taken"] = num_bart_rides
    results["total_cost"] = total_cost
    results["muni_only_fastpass_worth_it"] = not not_worth_m
    results["muni_bart_fastpass_worth_it"] = not not_worth_a

    return results


def parse_pdf(pdf_path):
    columns = [DATE, TRANSACTION_TYPE, LOCATION, ROUTE, PRODUCT, DEBIT, CREDIT, BALANCE]
    df = pd.DataFrame(columns=columns)
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
        None, print(f"Error extracting text from PDF: {e}")
    return df, None

def main():
    parser = argparse.ArgumentParser(description='Convert Clipper Card ride history PDF to CSV')
    parser.add_argument('pdf_path', help='Path to the Clipper Card transaction history PDF')
    parser.add_argument('-o', '--output', help='Output CSV file', default='clipper_transactions.csv')
    parser.add_argument('-fp', '--fastpass', help='Whether to print fastpass info', default='false')
    parser.add_argument('-w', '--worthit', help='Whether to check if fastpass would have been worth it', default='false')
    
    args = parser.parse_args()

    df, _err = parse_pdf(args.pdf_path)
    
    df.to_csv(args.output, index=False)

    if args.fastpass[0].lower() == 't':
        fastpass_info(df)

    if args.worthit[0].lower() == 't':
        is_fastpass_worth_it(df)

if __name__ == "__main__":
    main()
