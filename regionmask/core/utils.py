import six


def _maybe_to_dict(keys, values):
    """convert iterable to dict if necessary"""

    if not isinstance(values, dict):
        values = {key: value for key, value in zip(keys, values)}

    return values


def _create_dict_of_numbered_string(numbers, string):

    return {number: string + str(number) for number in numbers}


def _sanitize_names_abbrevs(numbers, values, default):

    if isinstance(values, six.string_types):
        values = _create_dict_of_numbered_string(numbers, values)
    elif values is None:
        values = _create_dict_of_numbered_string(numbers, default)
    else:

        assert len(numbers) == len(values)

        values = _maybe_to_dict(numbers, values)

    return values
