# import transform.xls
import sys
# import transform.xls
# import transform.csv

def type_transformation_module(type_name):
    """Get transformation module for resource of given type"""
    module_name = "transform.%s_transform" % type_name
    if module_name in sys.modules:
        return sys.modules[module_name]

    __import__(module_name)
    module = sys.modules[module_name]

    return module
