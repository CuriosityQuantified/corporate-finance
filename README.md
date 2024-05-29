# corporate-finance

This Flask application calculates the Return on Invested Capital (ROIC) for a company based on financial projections.

## Endpoints

- **POST /roic**: Calculate ROIC for a company.

## Example Request

```bash
curl -X POST http://localhost:5000/roic -H "Content-Type: application/json" -d '{
    "company_name": "Test Company",
    "revenue": [1000, 1200, 1500, 1800, 2000],
    "cogs": [500, 600, 700, 800, 900],
    "opex": [200, 220, 240, 260, 280],
    "tax_rate": 0.2,
    "nwc_changes": [50, 60, 70, 80, 90],
    "capex": [1000, 100, 100, 100, 100],
    "salvage_value": 500,
    "discount_rate": 0.1
}'

