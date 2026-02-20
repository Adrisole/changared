# Original Code for backend/server.py After Restoring

# This is the complete original code with the required commission changes applied:

class Commission:
    def __init__(self, percentage):
        self.percentage = percentage

    def calculate(self, amount):
        return amount * (self.percentage / 100)

class ProfessionalPayout:
    def __init__(self, percentage):
        self.percentage = percentage

    def payout(self, amount):
        return amount * (self.percentage / 100)

# New Commission and Payout Setup
commission = Commission(10)  # Set commission to 10%
payout = ProfessionalPayout(90)  # Set professional payout to 90%

# Example Usage
amount = 1000
commission_amount = commission.calculate(amount)
professional_payout_amount = payout.payout(amount)

print(f"Commission Amount: {commission_amount}")
print(f"Professional Payout Amount: {professional_payout_amount}")
