import argparse

from fetch_bio import get_bio_info, get_bio_info_batch

def arg_parser():
    parser = argparse.ArgumentParser(description="Fetch biological information from UniProt or BioPortal.")
    parser.add_argument("uri", type=str, nargs='+', help="The URI (list) of the biological entity to look up.")
    args = parser.add_argument_group('options')
    args.add_argument('-o', '--output', dest='json_output', default=None, 
                      help='Output JSON file path. If omitted, results are not saved to disk.')
    args.add_argument('-q', '--quiet', dest='print', action='store_false',
                       help='Suppress printing the result to the console.')
    return parser

def main():
    parser = arg_parser()
    args = parser.parse_args()
    # args.uri is ALWAYS a list because of nargs='+', so we check the length
    if len(args.uri) == 1:
        # 1. Fetch single item
        result = get_bio_info(args.uri[0],args.json_output)        
        # 2. Print if not quiet
        if args.print:
            print(result)
            
    else:
        # 1. Fetch batch items (the batch function handles its own JSON saving)
        result = get_bio_info_batch(args.uri, args.json_output)        
        # 2. Print if not quiet
        if args.print:
            print(result)

if __name__ == "__main__":
    main()