def dict_to_order(data_dict: dict):
    if all([not isinstance(i, dict) for i in data_dict.values()]):
        return list(data_dict)

    order_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            order_dict[key] = dict_to_order(data_dict[key])

    return order_dict