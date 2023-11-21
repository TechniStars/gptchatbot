def singleton(class_):
    """
    Decorator implementing Singleton Design Pattern for Class Objects
    Parameters
    ----------
    class_
    Returns
    -------
    object
        Instance of object
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Make just one instance of the class present at once
        """
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance
