def email_name(email_address):
    r = email_address.index("@")
    return "".join(l for l in email_address[:r] if l.isalpha())


def email_dot_to_comma(email_address):
    result = email_address.replace(".", ",")
    return result


def email_at_to_underscore_and_remove_dot(email_address):
    result = email_address.replace(".", "").replace("@", "_")
    return result
