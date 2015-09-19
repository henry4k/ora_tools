import xml.etree.ElementTree
import posixpath
import os.path
import sys
import ora_tools.virtual_fs as vfs
import ora_tools.node as node

def pump_io(input_file, output_file):
    while True:
        chunk = input_file.read(1024*1024)
        if not chunk or chunk == '':
            break
        output_file.write(chunk)

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
                    layer = node.from_xml(child)
                    layers.append(layer)

    def get_layers(self):
        return self.layers

    def _get_nested_layers(self, result_list, input_list):
        for layer in input_list:
            result_list.append(layer)
            try:
                self._get_nested_layers(result_list, layer.childs)
            except AttributeError:
                pass

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
        try:
            if len(layer.childs) > 0:
                raise RuntimeException('Blending not supported yet.')
        except AttributeError:
            pass
        extension = posixpath.splitext(layer.file_name)[1]
        destination_path = destination_prefix+extension
        with self.vfs.open(layer.file_name, 'r') as input_file:
            with open(destination_path, 'wb') as output_file:
                pump_io(input_file, output_file)
        return destination_path
