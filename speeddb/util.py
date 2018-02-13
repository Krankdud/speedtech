def is_admin(user):
    try:
        for role in user.roles:
            if role.name == 'admin':
                return True
    except AttributeError:
        return False
    return False