from collections import deque

def to_list(value):
    if isinstance(value, (list, tuple)):
        return value
    else:
        return [value]

def loaded_resource_map(resources, resource_map=None):
    resource_map = resource_map or {}
    if resources is None:
        return resource_map
    
    resources_queue = deque()
    resources_queue.extend(to_list(resources))
    
    while resources_queue:
        resource = resources_queue.pop()
        resource_class = resource.__class__
        
        if resource_class not in resource_map:
            resource_map[resource_class] = []
        
        resource_map[resource_class].append(resource)
    
        for field in resource_class.desc.related_fields:
            descriptor = getattr(resource_class, field.name)
            if descriptor.is_loaded(resource):
                related_resources = getattr(resource, field.name)
                resources_queue.extend(to_list(related_resources))
    
    return resource_map
