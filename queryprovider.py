import argparse
import importlib

from kitchenmusique import config, gproxy, providers


def instantiate_provider(name):
    provider_type = getattr(importlib.import_module("kitchenmusique.providers"), name)

    instance = provider_type()
    return instance


def main():

    parser = argparse.ArgumentParser(description="Kitchenmusique provider query processor")
    parser.add_argument("query",
                        metavar="query",
                        type=str,
                        help="Provider query string")

    parser.add_argument("--provider",
                        dest="provider",
                        action="store",
                        default="SputnikMusic",
                        help="Target provider")

    parser.add_argument("--tracklist",
                        action="store_true",
                        help="List all tracks that could be found in Google Play Music")

    args = parser.parse_args()

    provider = None

    try:
        provider = instantiate_provider(args.provider)

    except AttributeError as e:
        print("No such provider: '{0}'".format(args.provider))
        print(e)
        exit(0)

    finally:
        if provider is None:
            print("Failed to instantiate provider '{0}', exiting.".format(args.provider))
            exit(0)

    if args.tracklist:
        print("Fetching track names from Google Play Music, this may take some time...")
        for entry in provider.get_playlist(args.query):
            albumtracks = gproxy.Request(config.CONFIG_GPROXY_HOST, config.CONFIG_GPROXY_PORT) \
                .search_for_album() \
                .search_by_artist(entry.artist) \
                .search_by_album(entry.album) \
                .get()

            for song in albumtracks:
                print(song.title)

    else:
        for entry in provider.get_playlist(args.query):
            print("{0} - {1}".format(entry.artist, entry.album))


if __name__ == "__main__":
    main()
