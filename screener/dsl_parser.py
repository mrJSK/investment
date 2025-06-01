# screener/dsl_parser.py

from lark import Lark, Transformer, v_args, Token

# 1. Grammar Definition

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
               | indicator                      -> indicator_expr

    ?indicator: timeframe INDICATOR "(" [params] ")"   -> indicator_timeframe
              | INDICATOR "(" [params] ")"            -> indicator_no_timeframe
              | CANDLESTICK "(" ")"                   -> candlestick_pattern
    postfix: "." ("macd" | "signal" | "hist")  -> indicator_expr

    ?params: param ("," param)*
    ?param: FIELD
          | value
          | indicator     // allow indicators as params for advanced math, e.g. SMA(EMA(...), 20)
          | math_expr

    ?math_expr: indicator MATHOP indicator     -> math_indicator
              | indicator MATHOP value        -> math_value
              | value MATHOP indicator        -> value_math
              | value MATHOP value            -> value_value

    ?value: NUMBER

    // --- Terminals ---

    LOGICAL: "and"i | "or"i
    COMPOP: ">" | "<" | ">=" | "<=" | "==" | "!=" | "above"i | "below"i
    CROSSOP: "crosses above"i | "crosses below"i
    MATHOP: "+" | "-" | "*" | "/" | "^"
    timeframe: /(daily|weekly|monthly|1min|5min|15min|30min|1h|4h)/i
    INDICATOR: /(SMA|EMA|WMA|DEMA|TEMA|KAMA|RSI|MACD|ATR|NATR|OBV|MFI|BBANDS|ADX|STOCH|CCI|ROC|CMO|VWAP|STDDEV|VAR|AVGPRICE|MEDPRICE|TYPPRICE|WCLPRICE|MA|AVG|SUM|MAX|MIN|DIV|SUB|MUL|POW)/i
    FIELD: /(open|high|low|close|volume)/i
    CANDLESTICK: /(CDL\w+|Hammer|Doji|MorningStar|EveningStar)/i
    NUMBER: /[0-9]+(\.[0-9]+)?/

    %import common.WS
    %ignore WS
"""

parser = Lark(query_grammar, start='start', parser='lalr')

# 2. AST Transformer

class QueryTransformer(Transformer):

    def part_access(self, items):
        return str(items[0])
    
    def logical_expr(self, items):
        return {
            "type": "logical",
            "op": str(items[1]).lower(),
            "left": items[0],
            "right": items[2],
        }

    def not_expr(self, items):
        return {"type": "not", "expr": items[0]}

    def indicator_timeframe(self, items):
        tf = str(items[0])
        ind = str(items[1])
        
        # Check if the last item is a string (e.g., "macd", "signal", "hist") for part
        part = items[-1] if len(items) > 2 and isinstance(items[-1], str) else None
        # All items between index 2 and end (excluding part if it exists) are params
        params = items[2:-1] if part else items[2:]

        return {
            "type": "indicator",
            "timeframe": tf.lower(),
            "indicator": ind.upper(),
            "params": params,
            "part": part
        }

    def indicator_no_timeframe(self, items):
        ind = str(items[0])

        part = items[-1] if len(items) > 1 and isinstance(items[-1], str) else None
        params = items[1:-1] if part else items[1:]

        return {
            "type": "indicator",
            "timeframe": "default",
            "indicator": ind.upper(),
            "params": params,
            "part": part
        }


    def candlestick_pattern(self, items):
        pattern = str(items[0])
        return {
            "type": "candlestick",
            "pattern": pattern.upper()
        }

    def indicator_compare(self, items):
        return {
            "type": "compare",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2],
        }

    def indicator_value_compare(self, items):
        return {
            "type": "compare",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2],
        }

    def indicator_cross(self, items):
        return {
            "type": "cross",
            "op": str(items[1]).lower(),
            "left": items[0],
            "right": items[2],
        }

    def indicator_cross_value(self, items):
        return {
            "type": "cross",
            "op": str(items[1]).lower(),
            "left": items[0],
            "right": items[2],
        }

    def indicator_expr(self, items):
        # Single indicator (for highlighting, signals, etc)
        return items[0]

    def math_indicator(self, items):
        return {
            "type": "math",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2]
        }

    def math_value(self, items):
        return {
            "type": "math",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2]
        }

    def value_math(self, items):
        return {
            "type": "math",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2]
        }

    def value_value(self, items):
        return {
            "type": "math",
            "op": str(items[1]),
            "left": items[0],
            "right": items[2]
        }

    def params(self, items):
        return list(items)

    def param(self, items):
        return items[0]

    def value(self, items):
        return float(items[0])

    def FIELD(self, token):
        return str(token).lower()

    def NUMBER(self, token):
        return float(token)

    def INDICATOR(self, token):
        return str(token).upper()

    def TIMEFRAME(self, token):
        return str(token).lower()

    def CANDLESTICK(self, token):
        return str(token)

# 3. Main parse function

def parse_query(query_string):
    tree = parser.parse(query_string)
    return QueryTransformer().transform(tree)
