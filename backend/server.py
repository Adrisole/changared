# Original Code for backend/server.py
# Updated commission calculations

# Calculates commission based on sales
# 10% Commission
COMMISSION_RATE_1 = 0.1
# 90% Commission
COMMISSION_RATE_2 = 0.9

# Function to calculate commission

def calculate_commission(sale_amount):
    return sale_amount * COMMISSION_RATE_1

# Function to calculate another type of commission

def calculate_other_commission(sale_amount):
    return sale_amount * COMMISSION_RATE_2

# Other original code remains unchanged...