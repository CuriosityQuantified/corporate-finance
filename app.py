
from dataclasses import dataclass
from typing import List
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, fields, marshal_with
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

@dataclass
class CompanyFinancials:
    company_name: str
    revenue: List[float]
    cogs: List[float]
    opex: List[float]
    tax_rate: float
    nwc_changes: List[float]
    capex: List[float]
    salvage_value: float
    discount_rate: float

    def __post_init__(self):
        assert len(self.revenue) == 5, "Revenue projections must cover 5 years"
        assert len(self.cogs) == 5, "COGS projections must cover 5 years"
        assert len(self.opex) == 5, "OPEX projections must cover 5 years"
        assert 0 <= self.tax_rate <= 1, "Tax rate must be between 0 and 1"
        assert len(self.nwc_changes) == 5, "NWC change projections must cover 5 years"
        assert len(self.capex) == 5, "CAPEX projections must cover 5 years"
        assert self.discount_rate > 0, "Discount rate must be greater than 0"

def calculate_ebit(revenue: float, cogs: float, opex: float) -> float:
    return revenue - cogs - opex

def calculate_nopat(ebit: float, tax_rate: float) -> float:
    return ebit * (1 - tax_rate)

def calculate_nopat_for_year(financials: CompanyFinancials, year: int) -> float:
    ebit = calculate_ebit(financials.revenue[year], financials.cogs[year], financials.opex[year])
    return calculate_nopat(ebit, financials.tax_rate)

def calculate_invested_capital_for_year(financials: CompanyFinancials, year: int) -> float:
    return financials.capex[year] - financials.nwc_changes[year]

def calculate_pv(values: List[float], discount_rate: float) -> List[float]:
    return [values[i] / (1 + discount_rate)**i for i in range(len(values))]

def calculate_roic(financials: CompanyFinancials) -> float:
    nopat = [calculate_nopat_for_year(financials, i) for i in range(5)]
    invested_capital = [calculate_invested_capital_for_year(financials, i) for i in range(5)]
    
    nopat[-1] += financials.salvage_value
    
    pv_nopat = calculate_pv(nopat, financials.discount_rate)
    pv_invested_capital = calculate_pv(invested_capital, financials.discount_rate)
    
    roic = sum(pv_nopat) / sum(pv_invested_capital)
    
    return roic

resource_fields = {
    'company_name': fields.String,
    'roic': fields.Float
}

class ROICCalculator(Resource):
    @marshal_with(resource_fields)
    def post(self):
        try:
            data = request.get_json()
            logger.info("Received data: %s", data)
            financials = CompanyFinancials(**data)
            roic = calculate_roic(financials)
            logger.info("Calculated ROIC: %s for company: %s", roic, financials.company_name)
            return {'company_name': financials.company_name, 'roic': roic}, 200
        except AssertionError as e:
            logger.error("Assertion error: %s", e)
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            return {'error': 'An unexpected error occurred: ' + str(e)}, 500

api.add_resource(ROICCalculator, '/roic')

if __name__ == '__main__':
    app.run(debug=True)
