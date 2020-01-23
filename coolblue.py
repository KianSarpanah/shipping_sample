from datetime import datetime
import json
from collections import OrderedDict
from order_size import *


def get_order(obj):
    '''
        :brief reading input_data/order
    '''
    try:
        obj['Order'] = json.loads(obj['input'])
    except:
        raise ValueError('Error! The input_data formate is not a proper json formate!')
    
    del obj['input']


def verification_order_objs(obj, output=None):
    '''
        :brief verifing if objects in the input_data/order are valid
    '''
    if output is None:
        output = []
    try:
        # check if values exist and are not list
        output = list(map(lambda x: bool(obj['Order'].get(x, 0)), ["products", "order_timestamp", "order_id"]))
    except Exception:
        raise ValueError

    obj['verification'] = output


def get_order_params(obj, products_pricing_items=None):
    '''
        :brief Getting all parameters in order, which based on requirements are order_timestamp, order_id, and 
            the largest product_size between all products
    '''
    if products_pricing_items is None:
        products_pricing_items = []

    # numerizing pricing_items('XS', 'S', 'M', 'L' etc.) for further usages
    obj['dict_pricing_items'] = {v: k for k, v in enumerate(obj['pricing_items'])}
    product_ok, timestamp_ok, order_id_ok = obj['verification']

    if product_ok:
        # get all the pricing_items(in our case,all the costs are based on 'size') from all selected products in an order
        products_pricing_items = [i.get(obj['pricing_var']) for i in obj.get('Order').get('products', []) if i.get(obj['pricing_var']) and i.get(obj['pricing_var']) in obj['dict_pricing_items']]

    
    # get the largest product_size between all available products in an order
    obj['largest_pricing_item'] = max(products_pricing_items, key=obj['dict_pricing_items'].get) if products_pricing_items else None
    

    # if order_timestamp takes None, then return a valid time formate 
    if timestamp_ok:
        obj['order_timestamp'] = datetime.fromtimestamp(obj['Order']["order_timestamp"]).date()
    else:
        obj['order_timestamp'] = datetime.fromtimestamp(0).date()

    # check if the order has an id
    if not order_id_ok:
        raise ValueError('The order_id is not valid!')
    obj['order_id'] = obj['Order']["order_id"]
    del obj['Order']


def get_cost_settings(obj, all_settings=None):
    '''
        :brief Get the cost_settings 
    '''
    if all_settings is None:
        all_settings = []
    try:
        # just to make sure the last interval is not missing
        last_interval = {'start_date': datetime.strftime(datetime.now(), '%Y-%m-%d')}
        boundary = dict(list(obj['cost_settings'][0].items()) + list(last_interval.items()))
        all_settings = zip(obj['cost_settings'], obj['cost_settings'][1:]+[boundary])
    except:
        if not all_settings:
            raise ValueError('The cost_settings are not valid!')

    obj['all_settings'] = all_settings


def write_jsony_costs(obj, result=None):
    '''
        :brief Prepare dictionary to print out costs and order_ids in a json formate
        :param result: the dictionary for printting out the costs and order_id's
    '''

    # using OrderedDict dictionary to preserve order of keys
    if result is None:
        result = OrderedDict()
    temp = None
    for iset, next_iset in obj['all_settings']:
        start_date = datetime.strptime(iset["start_date"], '%Y-%m-%d').date()
        next_start_date = datetime.strptime(next_iset["start_date"], '%Y-%m-%d').date()

        # check conditions and break out as soon as a match happens
        if start_date <= obj['order_timestamp'] < next_start_date and obj.get('largest_pricing_item') == iset.get(obj['cost_item']):
            result["costs"] = float(iset["costs"])
            result["order_id"] = int(obj['order_id'])
            break

        # if the conditions to be met partially(where purchases are not in the interval but the size is), then take the latest cost settings 
        elif obj['order_timestamp'] < start_date and obj.get('largest_pricing_item') == iset.get(obj['cost_item']):
            temp = float(iset["costs"])

        elif obj['order_timestamp'] < next_start_date and obj.get('largest_pricing_item') != iset.get(obj['cost_item']):
            result["costs"] = temp
            result["order_id"] = int(obj['order_id'])

        # if no match happens at the end, then initialize the dictionary with None
        else:
            result["costs"] = None
            result["order_id"] = int(obj['order_id'])

    del obj['cost_settings']
    obj['result'] = json.dumps(result)

    print(obj['result'])


def main_func(input_data, settings):
    """
    :brief this is the main function. As tried to use pipline pattern, so an object
        created which is called coolblue_data and all required data pass using this object.
        At the end the result attribute for this object will be printed in the final stage.
    :param input_data: HackerRank Source Input
    :param settings: Hardcoded Cost Settings -- this won't be like this in production ;)
    """
    
    coolblue_data = {
        'input': input_data,
        'cost_settings': settings,
        'pricing_var': 'product_size',
        'pricing_items': ['XS', 'S', 'M', 'L','XL','XXL', 'XXXL'],
        'cost_item': "size"
    }

    all_procsses = [
        get_order,
        verification_order_objs,
        get_order_params,
        get_cost_settings,
        write_jsony_costs]


    for process in all_procsses:
        process(coolblue_data)


main_func(input_json, cost_settings)


