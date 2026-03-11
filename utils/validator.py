def validate_list(expected, actual, field_name):

    missing = []

    for value in expected:
        if value not in actual:
            missing.append(value)

    if missing:
        raise AssertionError(
            f"\n{field_name} Validation Failed\n"
            f"Expected : {expected}\n"
            f"Actual   : {actual}\n"
            f"Missing  : {missing}"
        )