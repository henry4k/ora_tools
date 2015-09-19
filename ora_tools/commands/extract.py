import argparse
import ora_tools as ora

def run(prog, description, args):
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('file')
    parser.add_argument('layer')
    parser.add_argument('prefix')

    args = parser.parse_args(args)

    reader = ora.OraFileReader(args.file)
    layer = reader.get_layer_by_name(args.layer)
    if not layer:
        raise RuntimeException('Can\'t find layer.')
    exported_file = reader.export_layer(layer, args.prefix)
    print(exported_file)
