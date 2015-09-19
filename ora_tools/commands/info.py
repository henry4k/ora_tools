import argparse
import ora_tools as ora

def run(prog, description, args):
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('file')

    args = parser.parse_args(args)

    reader = ora.OraFileReader(args.file)
    print(str.format('width: {}',reader.width))
    print(str.format('height: {}',reader.height))
    print('layers:')
    for layer in reader.get_nested_layers():
        print(str.format('  {}', layer.get_path()))
