def find_in_list_dicts(list_dicts, key_dict, value):
    element_dict = None
    for dict in list_dicts:
        if dict[key_dict] == value:
            element_dict = dict
            break
    return element_dict
        