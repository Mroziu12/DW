# utils/credit_bias_config.py

GENDER_RISK_ADJUSTMENT = {
    "M": -1.0,  # Men get lower risk
    "F": 0.5
}

CHILDREN_RISK_ADJUSTMENT = {
    0: -0.5,
    1: 0.0,
    2: 0.2,
    3: 0.4,
    "default": 0.6
}

EDUCATION_RISK_ADJUSTMENT = {
    "Higher education": -1.0,
    "Secondary": 0.2,
    "Incomplete higher education": 0.4,
    "default": 0.5
}

INCOME_RISK_SCALING = {
    "scale_factor": -0.00005,  # Each PLN increases chance of lower risk
    "max_adjustment": -1.5
}

AGE_RISK_ADJUSTMENT = [
    {"min": 18, "max": 25, "adjustment": 0.8},
    {"min": 26, "max": 35, "adjustment": 0.3},
    {"min": 36, "max": 50, "adjustment": -0.3},
    {"min": 51, "max": 65, "adjustment": -0.6},
    {"min": 66, "max": 100, "adjustment": -0.2}
]

BASE_RISK_RANGE = (4.5, 6.5)
