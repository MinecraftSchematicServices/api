from abc import ABC, ABCMeta, abstractmethod
from inspect import signature
from inputs import BaseInput
from functools import wraps


def handle_inputs(func):
    @wraps(func)
    def wrapper(cls, **kwargs):
        sig = signature(func.__func__)
        params = sig.parameters
        for name, param in params.items():
            if name == "cls":
                continue
            if name in kwargs and kwargs[name] is not None:
                input_obj = param.default
                if not isinstance(input_obj, BaseInput):
                    raise TypeError(f"Invalid input type for {name}")
                value = kwargs[name]
                validated_value = input_obj.validate(value)
                kwargs[name] = validated_value
            elif param.default is not None and isinstance(param.default, BaseInput):
                if param.default.default is not None:
                    kwargs[
                        name
                    ] = (
                        param.default.default
                    ) 
                else:
                    raise TypeError(f"Missing required argument: {name}")
            else:
                raise TypeError(f"Missing required argument: {name}")
        return func.__func__(cls, **kwargs)

    return wrapper


class MetaGenerator(ABCMeta):
    def __new__(cls, name, bases, class_dict):
        if "generate" in class_dict:
            class_dict["generate"] = classmethod(handle_inputs(class_dict["generate"]))
        return super().__new__(cls, name, bases, class_dict)
    
class GeneratorMetaData:
    def __init__(self, description=None, author=None, socials=None, tags=[], categories=[]):
        self.description = description
        self.author = author
        self.socials = socials or {}
        self.tags = tags
        self.categories = categories
    def to_dict(self):
        dict_data = {}
        if self.description:
            dict_data["description"] = self.description
        if self.author:
            dict_data["author"] = self.author
        if self.socials:
            dict_data["socials"] = self.socials
        if self.tags:
            dict_data["tags"] = self.tags
        if self.categories:
            dict_data["categories"] = self.categories
        return dict_data

class BaseGenerator(ABC, metaclass=MetaGenerator):
    meta_data = GeneratorMetaData()
    
    @abstractmethod
    def generate(cls, **kwargs):
        pass

    @classmethod
    def serialize_inputs(cls):
        func = cls.generate
        sig = signature(func)
        serialized_inputs = {}
        for name, param in sig.parameters.items():
            if name == "cls":
                continue
            
            if not isinstance(param.default, BaseInput):
                continue
            serialized_inputs[name] = param.default.to_dict()
        return serialized_inputs
    
    @classmethod
    def to_dict(cls):
        serialized_data = {
            "meta_data": cls.meta_data.to_dict(),
            "inputs": cls.serialize_inputs()
        }
        return serialized_data
