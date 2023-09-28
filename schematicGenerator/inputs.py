

class BaseInput:
    def __init__(self, default=None, description=""):
        self.default = default
        self.description = description

    def validate(self, value):
        raise NotImplementedError

    def to_dict(self):
        data = {k: v for k, v in vars(self).items() if v is not None}
        data["type"] = self.__class__.__name__
        return data

class IntInput(BaseInput):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        if not isinstance(value, int):
            raise ValueError(f"Expected an integer, got {type(value)}")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value should be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value should be <= {self.max_value}")
        return value

class BoolInput(BaseInput):
    def validate(self, value):
        if not isinstance(value, bool):
            raise ValueError(f"Expected a boolean, got {type(value)}")
        return value
    
# a set input only accepts values from a set
# it isn't made to be used directly, but rather as a base class for other inputs like the BlockInput
class  SetInput(BaseInput):
    def __init__(self, allowed_values=None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_values = allowed_values

    def validate(self, value):
        if self.allowed_values is not None and value not in self.allowed_values:
            raise ValueError(f"Value '{value}' is not allowed. Allowed values are: {', '.join(self.allowed_values)}")

        return value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "allowed_values": self.allowed_values
        })
        return data
    

class BlockInput(BaseInput):
    pass

class StringInput(BaseInput):
    def __init__(self, min_length=None, max_length=None, allowed_values=None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.allowed_values = allowed_values

    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Expected a string, got {type(value).__name__}")

        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(f"String is too short. Minimum length is {self.min_length}")

        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(f"String is too long. Maximum length is {self.max_length}")

        if self.allowed_values is not None and value not in self.allowed_values:
            raise ValueError(f"Value '{value}' is not allowed. Allowed values are: {', '.join(self.allowed_values)}")

        return value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "min_length": self.min_length,
            "max_length": self.max_length,
            "allowed_values": self.allowed_values
        })
        return data
    
    
class ArrayInput(BaseInput):
    def __init__(self, element_type, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(element_type, BaseInput):
            raise TypeError("element_type must be an instance of BaseInput or its subclasses")
        self.element_type = element_type
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, values):
        if not isinstance(values, list):
            raise ValueError(f"Expected a list, got {type(values).__name__}")

        # Check min and max length constraints
        if self.min_length is not None and len(values) < self.min_length:
            # If default values are provided and can be used to fill up to min_length
            if self.default and len(self.default) + len(values) >= self.min_length:
                values.extend(self.default[len(values):self.min_length])
            else:
                raise ValueError(f"List is too short. Minimum length is {self.min_length}")

        if self.max_length is not None and len(values) > self.max_length:
            raise ValueError(f"List is too long. Maximum length is {self.max_length}")

        validated_values = []
        for value in values:
            validated_value = self.element_type.validate(value)
            validated_values.append(validated_value)

        return validated_values

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "element_type": self.element_type.to_dict(),
            "min_length": self.min_length,
            "max_length": self.max_length
        })
        return data

class DictInput(BaseInput):
    def __init__(self, input_dict, **kwargs):
        super().__init__(**kwargs)
        if not all(isinstance(input_type, BaseInput) for input_type in input_dict.values()):
            raise TypeError("All values in input_dict must be instances of BaseInput or its subclasses")
        self.input_dict = input_dict

    def validate(self, values):
        if not isinstance(values, dict):
            raise ValueError(f"Expected a dictionary, got {type(values).__name__}")

        validated_values = {}
        for key, input_type in self.input_dict.items():
            if key not in values:
                if input_type.default is not None:
                    validated_values[key] = input_type.default
                else:
                    raise ValueError(f"Missing required key: {key}")
            else:
                validated_value = input_type.validate(values[key])
                validated_values[key] = validated_value

        return validated_values

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "input_dict": {key: input_type.to_dict() for key, input_type in self.input_dict.items()}
        })
        return data

