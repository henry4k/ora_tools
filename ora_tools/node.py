def get_attribute(element, name, default, fn):
    value = element.get(name)
    if value:
        if fn:
            return fn(value)
        else:
            return value
    else:
        return default

class Node:
    def __init__(self, **kwargs):
        self.parent = None
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def get_path(self):
        if self.parent:
            return self.parent.get_path()+'/'+self.name
        else:
            return self.name

    def set_parent(self, parent):
        if self.parent:
            raise RuntimeError('Parent node may only be set once.')
        else:
            self.parent = parent

class Stack(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        self.childs = []

    def append_child(self, child_layer):
        child_layer.set_parent(self)
        self.childs.append(child_layer)

class Layer(Node):
    pass

def from_xml(element):
    e = element
    kwargs = dict()
    kwargs['name']         = e.get('name')
    kwargs['visible']      = e.get('visibility') != 'invisible'
    kwargs['opacity']      = get_attribute(e, 'opacity', 1.0, float)
    kwargs['composite_op'] = e.get('composite-op') or 'svg:src-over'

    node = None

    if e.tag == 'layer':
        kwargs['x']         = get_attribute(e, 'x', 0, int)
        kwargs['y']         = get_attribute(e, 'y', 0, int)
        kwargs['file_name'] = e.get('src')
        node = Layer(**kwargs)
    elif e.tag == 'stack':
        node = Stack(**kwargs)
        for child_element in element:
            child_node = from_xml(child_element)
            node.append_child(child_layer)
    else:
        raise RuntimeError('Unknown element.')

    return node
