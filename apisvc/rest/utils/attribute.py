NO_DEFAULT = object()

def xgetattr(obj, name, default=NO_DEFAULT):
    try:
        current = obj
        for attribute in name.split("."):
            current = getattr(current, attribute)
        result = current
    except AttributeError:        
        if default is NO_DEFAULT:
            raise
        else:
            result = default
    return result

def xsetattr(obj, name, value):
    names = name.split(".")
    attribute_name = names.pop()

    current = obj
    for attribute in names:
        current = getattr(current, attribute)
    
    return setattr(current, attribute_name, value)

