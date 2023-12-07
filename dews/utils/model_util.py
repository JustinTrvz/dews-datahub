class ModelUtil():
    
    @staticmethod
    def to_dict(model):
        # Add attributes
        result = {field.name: getattr(model, field.name) for field in model._meta.fields}

        # Add items from relationships/references
        for field in model._meta.fields:
            if field.is_relation and hasattr(model, field.name):
                related_instance = getattr(model, field.name)
                result[field.name] = related_instance.to_dict() if related_instance else None

        return result