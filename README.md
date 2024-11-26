# hypnospace_bot
Mastodon bot that posts quotes from the game Hypnospace Outlaw

## Usage

1. Create a Python virtual environment with the [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/) library.
2. Run `hypnospace_txt.py` while specifying arguments for (refer to the `--help` output below):
   - (Required) The path to a file containing [an access token](https://sohwatt.com/generating-a-token-on-mastodon/) with `write:statuses` permissions.
   - (Required) The API base URL for your Mastodon instance.
   - (Optional) A path to write out a log file.
   - (Optional) The log level to write at.

```shell
$ python hypnospace_txt.py --help
usage: hypnospace_txt.py [-h] --token-file TOKEN_FILE --api-base-url API_BASE_URL [--log-file LOG_FILE] [--log-level {DEBUG,INFO,WARN,ERROR,FATAL}] [--quiet]

options:
  -h, --help            show this help message and exit
  --token-file TOKEN_FILE
                        Path to file containing access token
  --api-base-url API_BASE_URL
                        Mastodon API base URL
  --log-file LOG_FILE   Path to log file
  --log-level {DEBUG,INFO,WARN,ERROR,FATAL}
                        Set log level (default: INFO)
  --quiet, -q           Don't log to stdout
```
