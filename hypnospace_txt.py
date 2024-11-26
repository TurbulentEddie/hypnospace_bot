import sys
import json
import time
import random
import logging
import argparse
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

import mastodon


QUOTE_FILE = Path("quotes.json")
LAST_50 = Path("last_50.json")
HASHTAGS = "#hypnospace #hypnospaceoutlaw"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", type=Path, required=True, help="Path to file containing access token")
    parser.add_argument("--api-base-url", required=True, help="Mastodon API base URL")
    parser.add_argument("--log-file", type=Path, help="Path to log file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR", "FATAL"], default="INFO", help="Set log level (default: %(default)s)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Don't log to stdout")
    return parser.parse_args()


def get_logger(args) -> logging.Logger:
    logger = logging.getLogger(__name__)
    if len(logger.handlers) > 0:
        return logger
    logger.setLevel(getattr(logging, args.log_level))
    handlers = []
    if not args.quiet:
        handlers.append(logging.StreamHandler(sys.stdout))
    if args.log_file:
        handlers.append(RotatingFileHandler(args.log_file, maxBytes=1024*1024, backupCount=1))
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    return logger


def get_quote(args: argparse.Namespace) -> Dict[str, str]:
    logger = get_logger(args)
    quotes = json.load(QUOTE_FILE.open())
    try:
        last50 = json.load(LAST_50.open())
    except IOError:
        last50 = []
    for _ in range(250):
        quote_ids = list(quotes.keys())
        quote_id = random.choice(quote_ids)
        if quote_id not in last50:
            break
    last50.append(quote_id)
    json.dump(last50[-50:], LAST_50.open("w"))
    logger.info(f'Using quote "{quote_id}"')
    return quotes[quote_id]


def toot(args: argparse.Namespace, quote: str, spoiler: str):
    logger = get_logger(args)
    api = mastodon.Mastodon(
        access_token=args.token_file.open().read().strip(),
        api_base_url=args.api_base_url
    )
    params = {
        "status": f"{quote}",
        "visibility": "public",
    }
    if spoiler:
        params["spoiler_text"] = spoiler
        params["visibility"] = "unlisted"
    if params["visibility"] == "public" and HASHTAGS:
        params["status"] = f"{params['status']}\n\n{HASHTAGS}"
    attempts = 5
    success = False
    for att in range(attempts):
        try:
            logger.info(f'Attempting to post "{quote}"')
            api.status_post(**params)
        except mastodon.errors.MastodonRatelimitError:
            if att < (attempts - 1):
                backoff = 30 * 2**att
                logger.info(f"Got rate limited, trying again in {backoff} seconds")
                time.sleep(backoff)
        except mastodon.errors.MastodonError:
            if att < (attempts - 1):
                backoff = 30 * (att+1)
                logger.exception(f"Got unexpected Mastodon error, trying again in {backoff} seconds")
                time.sleep(backoff)
        except Exception:
            logger.exception("Got unexpected error")
            sys.exit(1)
        else:
            success = True
            break
    if not success:
        logger.error(f"Could not post to Mastodon after {attempts} attempts, exiting.")
        sys.exit(1)


def main():
    args = parse_args()
    logger = get_logger(args)
    logger.debug(f"Got args: {args}")
    try:
        quote = get_quote(args)
        toot(args, **quote)
    except Exception:
        logger.exception("Got unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()
