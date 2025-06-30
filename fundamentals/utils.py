# fundamentals/utils.py
import logging

logger = logging.getLogger(__name__)

# Define Market Cap Thresholds (in Crores INR)
# These are approximate and can be adjusted based on official definitions or your preference.
LARGE_CAP_THRESHOLD = 20000 * 10**7  # > 20,000 Crores
MID_CAP_THRESHOLD = 5000 * 10**7   # > 5,000 Crores and <= 20,000 Crores
# Small Cap is <= 5,000 Crores

def get_market_cap_category(market_cap):
    """Categorizes a company based on its market capitalization."""
    if market_cap is None:
        return "Unknown"
    
    if market_cap > LARGE_CAP_THRESHOLD:
        return "Large Cap"
    elif market_cap > MID_CAP_THRESHOLD:
        return "Mid Cap"
    else:
        return "Small Cap"

def calculate_fundamental_score(fundamental_data):
    """
    Calculates a fundamental score (out of 10) for a company based on its latest fundamental data.
    
    Args:
        fundamental_data (FundamentalData object): The latest fundamental data for a company.
        
    Returns:
        float: A score between 0 and 10.
    """
    score = 0.0
    
    # Weights for each metric (can be adjusted)
    WEIGHT_ROE = 2.0
    WEIGHT_ROC = 2.0
    WEIGHT_DEBT_TO_EQUITY = 2.5
    WEIGHT_PE = 2.0
    WEIGHT_PROFIT_GROWTH = 1.5

    # 1. Return on Equity (ROE) - Higher is better (Max 2 points)
    if fundamental_data.roe is not None:
        if fundamental_data.roe >= 25:
            score += 2.0 * WEIGHT_ROE / 10 # Scale by weight
        elif fundamental_data.roe >= 20:
            score += 1.5 * WEIGHT_ROE / 10
        elif fundamental_data.roe >= 15:
            score += 1.0 * WEIGHT_ROE / 10
        elif fundamental_data.roe >= 10:
            score += 0.5 * WEIGHT_ROE / 10

    # 2. Return on Capital Employed (ROC) - Higher is better (Max 2 points)
    if fundamental_data.roc is not None:
        if fundamental_data.roc >= 25:
            score += 2.0 * WEIGHT_ROC / 10
        elif fundamental_data.roc >= 20:
            score += 1.5 * WEIGHT_ROC / 10
        elif fundamental_data.roc >= 15:
            score += 1.0 * WEIGHT_ROC / 10
        elif fundamental_data.roc >= 10:
            score += 0.5 * WEIGHT_ROC / 10

    # 3. Debt to Equity - Lower is better (Max 2.5 points)
    if fundamental_data.debt_to_equity is not None:
        if fundamental_data.debt_to_equity <= 0.2:
            score += 2.5 * WEIGHT_DEBT_TO_EQUITY / 10
        elif fundamental_data.debt_to_equity <= 0.5:
            score += 2.0 * WEIGHT_DEBT_TO_EQUITY / 10
        elif fundamental_data.debt_to_equity <= 1.0:
            score += 1.0 * WEIGHT_DEBT_TO_EQUITY / 10
        elif fundamental_data.debt_to_equity <= 2.0:
            score += 0.5 * WEIGHT_DEBT_TO_EQUITY / 10
            
    # 4. Stock P/E - Lower is often better for value (Max 2 points)
    # Adjust ranges based on what you consider "good" P/E for fundamentally strong companies
    if fundamental_data.stock_pe is not None and fundamental_data.stock_pe > 0: # Avoid zero/negative P/E issues
        if fundamental_data.stock_pe <= 15:
            score += 2.0 * WEIGHT_PE / 10
        elif fundamental_data.stock_pe <= 25:
            score += 1.5 * WEIGHT_PE / 10
        elif fundamental_data.stock_pe <= 40:
            score += 0.5 * WEIGHT_PE / 10
            
    # 5. Profit Growth (3 Years) - Higher is better (Max 1.5 points)
    if fundamental_data.profit_growth_3_years is not None:
        if fundamental_data.profit_growth_3_years >= 25:
            score += 1.5 * WEIGHT_PROFIT_GROWTH / 10
        elif fundamental_data.profit_growth_3_years >= 15:
            score += 1.0 * WEIGHT_PROFIT_GROWTH / 10
        elif fundamental_data.profit_growth_3_years >= 5:
            score += 0.5 * WEIGHT_PROFIT_GROWTH / 10

    # Normalize score to 0-10 (since raw sum might exceed 10 if weights are high, or be less if weights are low)
    # Max possible raw score with these weights: 2.5*2.5 + 2*2 + 2*2 + 1.5*2 = 6.25 + 4 + 4 + 3 = 17.25
    # Let's adjust the total divisor to scale it to 10 effectively
    MAX_POSSIBLE_SCORE_SUM = 2.5 + 2.0 + 2.5 + 2.0 + 1.5 # Sum of max points from each category without weights if scaled to 10
    # Let's normalize by maximum achievable with these weights
    normalized_score = (score / (WEIGHT_ROE/10 * 2.0 + WEIGHT_ROC/10 * 2.0 + WEIGHT_DEBT_TO_EQUITY/10 * 2.5 + WEIGHT_PE/10 * 2.0 + WEIGHT_PROFIT_GROWTH/10 * 1.5)) * 10
    
    return round(max(0.0, min(10.0, normalized_score)), 2) # Ensure score is between 0 and 10

