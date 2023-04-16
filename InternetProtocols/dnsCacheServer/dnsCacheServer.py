from domain.dnsServer import DNSServer
from argparse import ArgumentParser


def config_argparse(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("-d", "--debug", action="store_true",
                            dest="debug", help="При указании запускает в debug режиме")


def main():
    arg_parser = ArgumentParser()
    config_argparse(arg_parser)
    args = arg_parser.parse_args()

    server = DNSServer(debug=args.debug)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nsaving cache...")
        server.save_cache()
        print("cache has been saved.")

    input("\nPress Enter for exit...")


if __name__ == "__main__":
    print("working...\n")
    main()
