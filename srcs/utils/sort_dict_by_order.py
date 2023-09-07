def sort_dict_by_order(data_dict: dict, order_dict: dict):
    """
        :exception Key error: order dict contains element that is not in data dict
    """
    for key, value in order_dict.items():
        if key not in data_dict:
            raise KeyError(key)

        if isinstance(value, dict):
            for x in value:
                if isinstance(data_dict[key][x], dict):
                    continue
                cause = data_dict[key][x]
                raise TypeError(f"{cause} {type(cause)} instance is unsortable")
        actual_order = list(value)
        actual_order.extend(x for x in data_dict[key] if x not in value)
        data_dict[key] = {
            item: data_dict[key][item] for item in actual_order
        }
        if isinstance(value, dict):
            # If the value is a dictionary, recursively sort it
            sort_dict_by_order(data_dict[key], value)


# test
def main():
    # Your data dictionary
    data_dict = {
        "domains": {
            "calyx_crimson": {
                "preservation": "data",
                "hunt": "data",
                "abundance": "data",
                "erudition": "data",
                "harmony": "data",
                "nihility": "data",
                "destruction": {
                    "subitem1": "data",
                    "subitem2": "data"
                }
            },
            "other_domain": {
                # Other domain data here
            }
        }
    }

    # Your order dictionary
    order_dict = {
        "domains": {
            # "calyx_crimson": [
            #     "destruction",
            #     "preservation",
            #     "hunt",
            #     "abundance",
            #     "erudition",
            #     "harmony",
            # ]
            "calyx_crimson": {
                "destruction": {
                    "subitem1": ["data"]
                }
            }
        }
    }

    try:
        # Sort the data dictionary by order
        sort_dict_by_order(data_dict, order_dict)

        # Print the sorted data dictionary
        import json
        print(json.dumps(data_dict, indent=4))
    except KeyError as e:
        print(f"KeyError: '{e}' in order_dict not found in data_dict.")


if __name__ == "__main__":
    main()
