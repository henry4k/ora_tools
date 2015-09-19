#!/usr/bin/env python2
import xml.etree.ElementTree
import posixpath
import os.path
import sys
import ora_tools.virtual_fs as vfs

def pump_io(input_file, output_file):
    while True:
        chunk = input_file.read(1024*1024)
        if not chunk or chunk == '':
            break
        output_file.write(chunk)

def get_attribute(element, name, default, fn):
    value = element.get(name)
    if value:
        if fn:
            return fn(value)
        else:
            return value
    else:
        return default

class OraLayer:
    def __init__(self, **kwargs):
        self.childs = []
        self.parent = None
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @staticmethod
    def from_xml(element):
        e = element
        layer = OraLayer(
            name = e.get('name'),
            visible = e.get('visibility') != 'invisible',
            opacity = get_attribute(e, 'opacity', 1.0, float),
            composite_op = e.get('composite-op') or 'svg:src-over',
            x = get_attribute(e, 'x', 0, int),
            y = get_attribute(e, 'y', 0, int),
            file_name = e.get('src'))
        for child_element in element:
            if child_element.tag == 'layer' or child_element.tag == 'stack':
                child_layer = OraLayer.from_xml(child_element)
                layer.append_child(child_layer)
        return layer

    def get_path(self):
        if self.parent:
            return self.parent.get_path()+'/'+self.name
        else:
            return self.name

    def set_parent(self, parent):
        if self.parent:
            raise RuntimeException('Layer may only set parent once.')
        else:
            self.parent = parent

    def append_child(self, child_layer):
        child_layer.set_parent(self)
        self.childs.append(child_layer)

class OraFileReader:
    def __init__(self, file_name):
        if os.path.isdir(file_name):
            self.vfs = vfs.DirectoryFileSystem(file_name, 'r')
        else:
            self.vfs = vfs.ZipFileSystem(file_name, 'r')
        if not self._is_valid():
            raise RuntimeError('Mimetype verification failed.')
        self._read_xml()

    def close(self):
        self.vfs.close()
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _is_valid(self):
        try:
            with self.vfs.open('mimetype', 'r') as mimetype:
                return mimetype.readline() == 'image/openraster'
        except KeyError:
            return False

    def _read_xml(self):
        with self.vfs.open('stack.xml', 'r') as xml_file:
            tree = xml.etree.ElementTree.parse(xml_file)
            image = tree.getroot()
            if image.tag != 'image':
                raise RuntimeException('Expected image element.')

            self.width  = int(image.get('w'))
            self.height = int(image.get('h'))

            stack = image.find('stack')
            layers = []
            self.layers = layers
            for child in stack:
                if child.tag == 'layer' or child.tag == 'stack':
                    layer = OraLayer.from_xml(child)
                    layers.append(layer)

    def get_layers(self):
        return self.layers

    def _get_nested_layers(self, result_list, input_list):
        for layer in input_list:
            result_list.append(layer)
            self._get_nested_layers(result_list, layer.childs)

    def get_nested_layers(self):
        results = []
        self._get_nested_layers(results, self.layers)
        return results

    def get_layer_by_name(self, name):
        for layer in self.get_nested_layers():
            if layer.name == name:
                return layer

    def get_layer_by_path(self, path):
        for layer in self.get_nested_layers():
            if layer.get_path() == path:
                return layer

    def export_layer(self, layer, destination_prefix):
        if len(layer.childs) > 0:
            raise RuntimeException('Blending not supported yet.')
        else:
            extension = posixpath.splitext(layer.file_name)[1]
            destination_path = destination_prefix+extension
            with self.vfs.open(layer.file_name, 'r') as input_file:
                with open(destination_path, 'wb') as output_file:
                    pump_io(input_file, output_file)
            return destination_path
