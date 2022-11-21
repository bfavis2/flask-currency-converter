from flask import Flask, jsonify, Response, request
import requests
from . import secrets # used to store api keys and other secrets -- need to create your own
# NOTE: you will need to add your own api key for currencyapi (https://freecurrencyapi.net/#documentationSection)
# to get this to work
# just create a file in the same folder called `secrets.py` and add a variable called `CURRENCYAPI_APIKEY`
# set the variable to your api key

'''
Example Usage
http://127.0.0.1:5000/converter?base_currency=GBP&to_currency=USD
http://127.0.0.1:5000/converter?base_currency=EUR&to_currency=GBP&amount=123

'''

app = Flask(__name__)

@app.route('/converter', methods=['GET'])
def convert_currency() -> Response:
    '''https://freecurrencyapi.net/#documentationSection
    Returns the conversation rate from one currency to another.

    Query Parameters:
        base-currency (str): The base or starting currency in ISO 4217 country code format. Current version only supports USD, GBP, and EUR.
        to-currency (str): The currency to convert into in ISO 4217 country code format. Current version only supports USD, GBP, and EUR.
        [amount (float)]: OPTIONAL - The amount in the base currency to convert

    Returns:
        JSON Response:
            conversion_rate (float): The amount in to-currency that 1 unit of base-currency converts into.
            [converted_amount (float)]: Only returned if amount is passed in. The amount * conversion_rate rounded to 2 decimal places.
            user_input (JSON): The query parameters passed in by the user.

    '''

    args = request.args

    base_currency = args.get('base-currency', '')
    to_currency = args.get('to-currency', '')
    base_amount = args.get('amount', 1)

    if validation_response := validation_check(base_currency, to_currency, base_amount, args):
        return validation_response

    conversion_rate = get_conversion_rate(base_currency, to_currency)

    response = {
        'conversion_rate': conversion_rate,
        'user_input': args,
    }
    
    # if an amount was passed in by the user, then also return back the converted amount
    if args.get('amount'):
        converted_amount = conversion_rate * float(base_amount)
        response['converted_amount'] = round(converted_amount, 2)

    return response

def validation_check(base_currency: str, to_currency: str, base_amount: str, user_input: dict) -> tuple:
    '''
    Validates the user's input to the converter API
    '''

    VALID_COUNTRIES = set(['USD', 'GBP', 'EUR'])
    
    # validate that the query parameters passed in are valid
    if not base_currency.upper() in VALID_COUNTRIES or not to_currency.upper() in VALID_COUNTRIES:
        error_response = {
            'error': 'Invalid or missing query parameters',
            'notes': 'Query parameters, base-currency and to-currency, are required. Values must be valid ISO 4217 country codes. Only USD, GBP, and EUR are currently supported.',
            'user_input': user_input
        }
        return jsonify(error_response), 400

    # if an amount is passed in, check if it's a number
    try:
        base_amount = float(base_amount)
    except ValueError:
        error_response = {
            'error': 'Invalid amount passed in',
            'notes': 'Make sure amount is a valid number.',
            'user_input': user_input
        }
        return jsonify(error_response), 400

    return tuple()
        
def get_conversion_rate(base_currency: str, to_currency: str) -> float:
    '''
    Calls an external API to get the current conversion rate. Uses currencyapi.

    Args:
        base_currency (str): The base or starting currency in ISO 4217 country code format.
        to_currency (str): The currency to convert into in ISO 4217 country code format.

    Returns:
        The conversion rate (float)

    '''

    endpoint = 'https://api.currencyapi.com/v3/latest'

    params = {
        'apikey': secrets.CURRENCYAPI_APIKEY,
        'base_currency': base_currency.upper(),
        'currencies': [to_currency.upper()]
    }
    
    r = requests.get(endpoint, params=params)

    '''
    example currencyapi response
    {
        "meta": {
            "last_updated_at": "2022-11-20T23:59:59Z"
        },
        "data": {
            "GBP": {
                "code": "GBP",
                "value": 0.841409
            }
        }
    }
    '''

    return r.json()['data'][to_currency.upper()]['value']
