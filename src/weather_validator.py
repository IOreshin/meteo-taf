
def exists(x):
    return x is not None and x != ""

def to_int(x):
    try:
        return int(x)
    except:
        return 0

def validate_data(data, rules):
    errors = []
    for rule in rules.get("checks", []):
        try:
            if eval(rule["condition"], {"exists" : exists, "to_int" : to_int}, data):
                errors.append(rule["message"])
        except Exception as e:
            errors.append(f"Ошибка в правиле: {rule['condition']} ({e})")
    
    return errors

def validate_codes(data, rules):
    errors = []
    weather_list = data.get("weather_events", [])

    for rule in rules.get("weather_code_rules", []):
        for code in weather_list:
            if rule["code"] == code:
                for cond in rule.get("conditions", []):
                    try:
                        if not eval(cond["check"], {}, data):
                            errors.append(cond["message"])
                    except Exception as e:
                        errors.append(f"Ошибка в правиле: {cond['check']} ({e})")

    return errors

def validate_all_data(data, rules):
    errors = []
    errors.extend(validate_data(data, rules))
    errors.extend(validate_codes(data, rules))
    return errors