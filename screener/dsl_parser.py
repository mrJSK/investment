# # screener/dsl_parser.py

# from lark import Lark, Transformer, v_args, Token

# # 1. Grammar Definition

# query_grammar = r"""
#     ?start: expr

#     ?expr: expr LOGICAL expr       -> logical_expr
#          | "not"i expr            -> not_expr
#          | "(" expr ")"
#          | comparison

#     ?comparison: indicator COMPOP indicator      -> indicator_compare
#                | indicator COMPOP value         -> indicator_value_compare
#                | indicator CROSSOP indicator    -> indicator_cross
#                | indicator CROSSOP value        -> indicator_cross_value
#                | indicator                      -> indicator_expr

#     ?indicator: timeframe INDICATOR "(" [params] ")"   -> indicator_timeframe
#               | INDICATOR "(" [params] ")"            -> indicator_no_timeframe
#               | CANDLESTICK "(" ")"                   -> candlestick_pattern
#     postfix: "." ("macd" | "signal" | "hist")  -> indicator_expr

#     ?params: param ("," param)*
#     ?param: FIELD
#           | value
#           | indicator     // allow indicators as params for advanced math, e.g. SMA(EMA(...), 20)
#           | math_expr

#     ?math_expr: indicator MATHOP indicator     -> math_indicator
#               | indicator MATHOP value        -> math_value
#               | value MATHOP indicator        -> value_math
#               | value MATHOP value            -> value_value

#     ?value: NUMBER

#     // --- Terminals ---

#     LOGICAL: "and"i | "or"i
#     COMPOP: ">" | "<" | ">=" | "<=" | "==" | "!=" | "above"i | "below"i
#     CROSSOP: "crosses above"i | "crosses below"i
#     MATHOP: "+" | "-" | "*" | "/" | "^"
#     timeframe: /(daily|weekly|monthly|1min|5min|15min|30min|1h|4h)/i
#     INDICATOR: /(SMA|EMA|WMA|DEMA|TEMA|KAMA|RSI|MACD|ATR|NATR|OBV|MFI|BBANDS|ADX|STOCH|CCI|ROC|CMO|VWAP|STDDEV|VAR|AVGPRICE|MEDPRICE|TYPPRICE|WCLPRICE|MA|AVG|SUM|MAX|MIN|DIV|SUB|MUL|POW)/i
#     FIELD: /(open|high|low|close|volume)/i
#     CANDLESTICK: /(CDL\w+|Hammer|Doji|MorningStar|EveningStar)/i
#     NUMBER: /[0-9]+(\.[0-9]+)?/

#     %import common.WS
#     %ignore WS
# """

# parser = Lark(query_grammar, start='start', parser='lalr')

# # 2. AST Transformer

# class QueryTransformer(Transformer):

#     def part_access(self, items):
#         return str(items[0])
    
#     def logical_expr(self, items):
#         return {
#             "type": "logical",
#             "op": str(items[1]).lower(),
#             "left": items[0],
#             "right": items[2],
#         }

#     def not_expr(self, items):
#         return {"type": "not", "expr": items[0]}

#     def indicator_timeframe(self, items):
#         tf = str(items[0])
#         ind = str(items[1])
        
#         # Check if the last item is a string (e.g., "macd", "signal", "hist") for part
#         part = items[-1] if len(items) > 2 and isinstance(items[-1], str) else None
#         # All items between index 2 and end (excluding part if it exists) are params
#         params = items[2:-1] if part else items[2:]

#         return {
#             "type": "indicator",
#             "timeframe": tf.lower(),
#             "indicator": ind.upper(),
#             "params": params,
#             "part": part
#         }

#     def indicator_no_timeframe(self, items):
#         ind = str(items[0])

#         part = items[-1] if len(items) > 1 and isinstance(items[-1], str) else None
#         params = items[1:-1] if part else items[1:]

#         return {
#             "type": "indicator",
#             "timeframe": "default",
#             "indicator": ind.upper(),
#             "params": params,
#             "part": part
#         }


#     def candlestick_pattern(self, items):
#         pattern = str(items[0])
#         return {
#             "type": "candlestick",
#             "pattern": pattern.upper()
#         }

#     def indicator_compare(self, items):
#         return {
#             "type": "compare",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2],
#         }

#     def indicator_value_compare(self, items):
#         return {
#             "type": "compare",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2],
#         }

#     def indicator_cross(self, items):
#         return {
#             "type": "cross",
#             "op": str(items[1]).lower(),
#             "left": items[0],
#             "right": items[2],
#         }

#     def indicator_cross_value(self, items):
#         return {
#             "type": "cross",
#             "op": str(items[1]).lower(),
#             "left": items[0],
#             "right": items[2],
#         }

#     def indicator_expr(self, items):
#         # Single indicator (for highlighting, signals, etc)
#         return items[0]

#     def math_indicator(self, items):
#         return {
#             "type": "math",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2]
#         }

#     def math_value(self, items):
#         return {
#             "type": "math",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2]
#         }

#     def value_math(self, items):
#         return {
#             "type": "math",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2]
#         }

#     def value_value(self, items):
#         return {
#             "type": "math",
#             "op": str(items[1]),
#             "left": items[0],
#             "right": items[2]
#         }

#     def params(self, items):
#         return list(items)

#     def param(self, items):
#         return items[0]

#     def value(self, items):
#         return float(items[0])

#     def FIELD(self, token):
#         return str(token).lower()

#     def NUMBER(self, token):
#         return float(token)

#     def INDICATOR(self, token):
#         return str(token).upper()

#     def TIMEFRAME(self, token):
#         return str(token).lower()

#     def CANDLESTICK(self, token):
#         return str(token)

# # 3. Main parse function

# def parse_query(query_string):
#     tree = parser.parse(query_string)
#     return QueryTransformer().transform(tree)

# screener/dsl_parser.py

from lark import Lark, Transformer, v_args, Token, Tree

# 1. Grammar Definition
# NOTE: The INDICATOR terminal regex needs to include all custom indicator names
# like MACD_LINE, MACD_SIGNAL, MACD_HIST, BB_UPPER, BB_MIDDLE, BB_LOWER, STOCH_K, STOCH_D, EFI etc.
# This is a simplified list; you should make it comprehensive.
# Alternatively, make INDICATOR a more generic identifier and validate in transformer.
# For now, adding the specific new ones.
query_grammar = r"""
    ?start: expr

    ?expr: expr LOGICAL expr       -> logical_expr
         | "not"i expr            -> not_expr
         | "(" expr ")"
         | comparison

    ?comparison: indicator COMPOP indicator      -> indicator_compare
               | indicator COMPOP value         -> indicator_value_compare
               | indicator CROSSOP indicator    -> indicator_cross
               | indicator CROSSOP value        -> indicator_cross_value
               | indicator                      // Allows an indicator to be a standalone expression

    // MODIFIED indicator rules to include optional part (dot notation)
    ?indicator: timeframe INDICATOR "(" [params] ")" [ "." PART_IDENTIFIER ] -> indicator_timeframe
              | INDICATOR "(" [params] ")" [ "." PART_IDENTIFIER ]            -> indicator_no_timeframe
              | CANDLESTICK "(" ")"                                           -> candlestick_pattern

    ?params: param ("," param)*
    ?param: FIELD               
          | value
          | indicator           
          # | math_expr        

    ?value: NUMBER

    // --- Terminals ---
    LOGICAL: "and"i | "or"i
    COMPOP: ">" | "<" | ">=" | "<=" | "==" | "!=" | "above"i | "below"i
    CROSSOP: "crosses above"i | "crosses below"i
    
    timeframe: /(daily|weekly|monthly|1min|5min|15min|30min|1h|4h)/i
    // UPDATED INDICATOR REGEX to include new custom/derived indicators
    INDICATOR: /(SMA|EMA|WMA|DEMA|TEMA|KAMA|RSI|MACDEXT|MACDFIX|ATR|NATR|OBV|MFI|ADX|STOCHF|STOCHRSI|CCI|ROC|CMO|VWAP|STDDEV|VAR|AVGPRICE|MEDPRICE|TYPPRICE|WCLPRICE|MA|AVG|SUM|MAX|MIN|DIV|SUB|MUL|POW|SAR|AD|ADOSC|APO|AROON|AROONOSC|BOP|CMF|DX|HT_DCPERIOD|HT_DCPHASE|HT_PHASOR|HT_SINE|HT_TRENDLINE|HT_TRENDMODE|LINEARREG|LINEARREG_ANGLE|LINEARREG_INTERCEPT|LINEARREG_SLOPE|MIDPOINT|MIDPRICE|MINMAX|MINMAXINDEX|PLUS_DI|PLUS_DM|PPO|ROCP|ROCR|ROCR100|SUB|TRIX|ULTOSC|WILLR|EFI|MY_CUSTOM_INDICATOR|MACD_LINE|MACD_SIGNAL|MACD_HIST|BB_UPPER|BB_MIDDLE|BB_LOWER|STOCH_K|STOCH_D)/i
    FIELD: /(open|high|low|close|volume)/i  
    CANDLESTICK: /(CDL\w+|Hammer|Doji|MorningStar|EveningStar)/i
    PART_IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/ 
    NUMBER: /[0-9]+(\.[0-9]+)?/

    %import common.WS
    %ignore WS
"""

# This should reflect the parts defined in builder.js INDICATOR_PARTS for validation
VALID_INDICATOR_PARTS = {
    "MACD": ["macd", "signal", "hist"], # For base MACD if .part syntax is used
    "BBANDS": ["upper", "middle", "lower", "bandwidth"], # For base BBANDS if .part syntax is used
    "STOCH": ["k", "d"] # For base STOCH if .part syntax is used
}

class QueryTransformer(Transformer):
    def logical_expr(self, items):
        return {"type": "logical", "op": str(items[1]).lower(), "left": items[0], "right": items[2]}

    def not_expr(self, items):
        return {"type": "not", "expr": items[0]}

    def _transform_params(self, params_tree_or_list_of_tokens):
        if not params_tree_or_list_of_tokens: return []
        actual_param_items = []
        if isinstance(params_tree_or_list_of_tokens, Tree) and params_tree_or_list_of_tokens.data == "params":
            actual_param_items = params_tree_or_list_of_tokens.children
        elif isinstance(params_tree_or_list_of_tokens, list):
            actual_param_items = params_tree_or_list_of_tokens
        
        processed_params = []
        for item in actual_param_items:
            if isinstance(item, Token): 
                if item.type == "NUMBER": processed_params.append(float(item.value))
                elif item.type == "FIELD": processed_params.append(str(item.value).lower())
                else: processed_params.append(str(item.value)) 
            else: 
                processed_params.append(item)
        return processed_params

    def _extract_indicator_details(self, items, has_timeframe):
        idx_offset = 1 if has_timeframe else 0
        indicator_name_token = items[idx_offset]
        indicator_name = str(indicator_name_token).upper()
        part_value = None
        
        params_start_idx = idx_offset + 2 # After INDICATOR and "("
        params_end_idx = -1 # Default: params go up to the closing parenthesis ")"

        if len(items) >= idx_offset + 4 and str(items[-2]) == "." and isinstance(items[-1], Token) and items[-1].type == "PART_IDENTIFIER":
            part_value = str(items[-1].value).lower()
            # Validate part only if the base indicator is one that supports .part syntax
            if indicator_name in VALID_INDICATOR_PARTS and part_value not in VALID_INDICATOR_PARTS[indicator_name]:
                raise ValueError(f"Invalid part '{part_value}' for base indicator '{indicator_name}'. Allowed: {VALID_INDICATOR_PARTS[indicator_name]}")
            params_end_idx = -3 
        
        params_candidate_list = items[params_start_idx:params_end_idx]
        processed_params = self._transform_params(params_candidate_list[0] if len(params_candidate_list) == 1 and isinstance(params_candidate_list[0], Tree) and params_candidate_list[0].data == "params" else params_candidate_list)

        return indicator_name, processed_params, part_value

    def indicator_timeframe(self, items):
        timeframe = str(items[0]).lower()
        indicator_name, processed_params, part_value = self._extract_indicator_details(items, has_timeframe=True)
        return {
            "type": "IndicatorCall", "timeframe": timeframe, "name": indicator_name,
            "arguments": processed_params, "part": part_value
        }

    def indicator_no_timeframe(self, items):
        indicator_name, processed_params, part_value = self._extract_indicator_details(items, has_timeframe=False)
        return {
            "type": "IndicatorCall", "timeframe": "daily", "name": indicator_name,
            "arguments": processed_params, "part": part_value
        }

    def candlestick_pattern(self, items):
        return {"type": "candlestick", "pattern": str(items[0]).upper()}

    def indicator_compare(self, items):
        return {"type": "compare", "op": str(items[1]), "left": items[0], "right": items[2]}

    def indicator_value_compare(self, items):
        right_val = items[2]
        if isinstance(right_val, Token) and right_val.type == 'NUMBER':
            right_val = float(right_val.value)
        return {"type": "compare", "op": str(items[1]), "left": items[0], "right": {"type": "NumberLiteral", "value": right_val} if isinstance(right_val, (int,float)) else right_val}

    def indicator_cross(self, items):
        return {"type": "cross", "op": str(items[1]).lower(), "left": items[0], "right": items[2]}

    def indicator_cross_value(self, items):
        right_val = items[2]
        if isinstance(right_val, Token) and right_val.type == 'NUMBER':
            right_val = float(right_val.value)
        return {"type": "cross", "op": str(items[1]).lower(), "left": items[0], "right": {"type": "NumberLiteral", "value": right_val} if isinstance(right_val, (int,float)) else right_val}

    def params(self, items): 
        return self._transform_params(items) 

    def param(self, items): 
        return items[0] 

    def value(self, items): 
        return {"type": "NumberLiteral", "value": items[0]} 

    def FIELD(self, token): 
        return str(token).lower() 

    def NUMBER(self, token):
        return float(token)

    def INDICATOR(self, token): return token 
    def TIMEFRAME(self, token): return token 
    def PART_IDENTIFIER(self, token): return token 
    def CANDLESTICK(self, token): return str(token)

parser = Lark(query_grammar, start='start', parser='lalr', transformer=QueryTransformer())

def parse_query(query_string):
    try:
        tree = parser.parse(query_string)
        return tree 
    except Exception as e:
        return {
            "type": "PARSE_ERROR", "error": f"Syntax Error: {str(e)}",
            "details": f"Could not parse query: '{query_string}'"
        }
