

class BaseInput:
    def __init__(self, default=None, description=""):
        self.default = default
        self.description = description

    def validate(self, value):
        return value

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
    
class ComplexInput(BaseInput):
    def __init__(self, real_default=0.0, imag_default=0.0, real_low_bound=-float("inf"), real_high_bound=float("inf"), imag_low_bound=-float("inf"), imag_high_bound=float("inf"), **kwargs):
        super().__init__(**kwargs)
        self.real_default = real_default
        self.imag_default = imag_default
        self.real_low_bound = real_low_bound
        self.real_high_bound = real_high_bound
        self.imag_low_bound = imag_low_bound
        self.imag_high_bound = imag_high_bound
        


    def validate(self, value):
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError("Expected a tuple or list with two elements for a complex number")
        real, imag = value
        if not isinstance(real, (int, float)) or not isinstance(imag, (int, float)):
            raise ValueError("Both real and imaginary parts should be numbers")
        return complex(real, imag)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "real_default": self.real_default,
            "imag_default": self.imag_default
        })
        return data
    

class BlockInput(BaseInput):
    # a block is a string that is prefixed with minecraft: and has a block name after it
    # for example: minecraft:stone
    def __init__(self, palette=None, **kwargs):
        super().__init__(**kwargs)
        self.palette = palette
        
    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Expected a string, got {type(value).__name__}")
        if not value.startswith("minecraft:"):
            raise ValueError(f"Expected a block, got {value}")
        if self.palette is not None and value not in self.palette:
            raise ValueError(f"Value '{value}' is not allowed. Allowed values are: {', '.join(self.palette)}")

        return value
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "palette": self.palette
        })
        return data

# this input is used to select one of the values from a options list
class SelectInput(BaseInput):
    def __init__(self, options=None, **kwargs):
        super().__init__(**kwargs)
        self.options = options

    def validate(self, value):
        if self.options is not None and value not in self.options:
            raise ValueError(f"Value '{value}' is not allowed. Allowed values are: {', '.join(self.options)}")

        return value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "options": self.options
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
    
class InputGroup(BaseInput):
    def __init__(self, inputs: dict, **kwargs):
        super().__init__(**kwargs)
        if not all(isinstance(input_type, BaseInput) for input_type in inputs.values()):
            raise TypeError("All values in inputs must be instances of BaseInput or its subclasses")
        self.inputs = inputs

    def validate(self, values):
        if not isinstance(values, dict):
            raise ValueError(f"Expected a list, got {type(values).__name__}")

        if len(values) != len(self.inputs):
            raise ValueError(f"Expected a list of length {len(self.inputs)}, got {len(values)}")

        validated_values = {}
        for key, input_type in self.inputs.items():
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
            "inputs": {key: input_type.to_dict() for key, input_type in self.inputs.items()}
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

