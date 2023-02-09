# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import os

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Replace YOUR_API_KEY with your own Alpha Vantage API key
api_key = open("secret.txt", "r").read()

# Get the ticker symbol from the user
ticker_symbol = input("Enter the ticker symbol of the company: ")

# Gathering all three financial statements
functions = ['INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']
financial_data = {}

for function in functions:
    # Specify the frequency of the data
    interval = 'annual'  # or 'quarter'

    # Send a request to the Alpha Vantage API to gather the financial data
    url = f'https://www.alphavantage.co/query?function={function}&symbol={ticker_symbol}&apikey={api_key}&interval={interval}'
    response = requests.get(url)

    # Check the response status code and the content of the response in case the API returns an error message
    if response.status_code != 200:
        print("Error: API request failed with status code", response.status_code)
        print(response.content)
        exit()

    try:
        financial_data[function] = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        print("Error: Failed to parse JSON data from API response")
        print(e)
        print(response.content)
        exit()

# Load the financial data into a pandas DataFrame
# financial_data = pd.DataFrame(financial_data)
# Example expense ratio (expenses as a proportion of revenue)
expense_ratio = 0.6

# Example growth rate
growth_rate = 0.03

financial_data = financial_data['INCOME_STATEMENT']['annualReports'][0]

financial_data['future_revenue'] = int(financial_data['totalRevenue']) * growth_rate *  5

financial_data['future_expenses'] = int(financial_data['totalRevenue']) * expense_ratio *  5

# Check if the data contains the column 'revenue'
# if "future_revenue" in financial_data.columns and "future_expenses" not in financial_data.columns:
#     financial_data["future_expenses"] = financial_data["future_revenue"] * expense_ratio
# if "totalRevenue" in financial_data.columns:
#     financial_data["future_revenue"] = financial_data["totalRevenue"].iloc[-1] * (1 + growth_rate) ** (range(1, len(financial_data) + 1))
# financial_data["future_expenses"] = financial_data["future_revenue"] * expense_ratio

# Assume a discount rate of 10%
discount_rate = 0.1

# Create an empty column for future cash flows
financial_data['future_cash_flows'] = None

# Calculate future cash flows based on projected financials
financial_data['future_cash_flows'] = financial_data['future_revenue'] - financial_data['future_expenses']

# Create an empty column for present value of future cash flows
financial_data['DCF_valuation'] = None

# Calculate the present value of future cash flows
financial_data['DCF_valuation'] = financial_data['future_cash_flows'] / (1 + discount_rate)

# Print the financial data with the new columns
print(financial_data)

# Sensitivity analysis on discount rate
discount_rates = np.linspace(0.05, 0.15, num=11)
valuations = []
for rate in discount_rates:
    valuations.append(financial_data['future_cash_flows'] / ((1 + rate)))

plt.plot(discount_rates, valuations)
plt.xlabel('Discount Rate')
plt.ylabel('Valuation')
plt.show()

# Sensitivity analysis on growth rate
growth_rates = np.linspace(0, 0.06, num=7)
valuations = []

for rate in growth_rates:
    financial_data['future_revenue'] = int(financial_data['totalRevenue']) * (1 + rate)
    financial_data['future_expenses'] = financial_data['future_revenue'] * expense_ratio
    financial_data['future_cash_flows'] = financial_data['future_revenue'] - financial_data['future_expenses']
    valuations.append(financial_data['future_cash_flows'] / ((1 + discount_rate)))



plt.plot(growth_rates, valuations)
plt.xlabel('Growth Rate')
plt.ylabel('Valuation')
plt.show()

# Report generation
report = {}
report['Discount Rate'] = discount_rate
report['Growth Rate'] = growth_rate
report['Expense Ratio'] = expense_ratio
report['Valuation'] = financial_data['DCF_valuation']

# Output the report to an excel file
# report_df = pd.DataFrame(report, index=[0])
# report_df.to_excel('DCF_Valuation_Report.xlsx')

print(report)


