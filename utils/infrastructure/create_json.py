import json
import sys
import os

"""
Creates local.settings.json file for Azure Function App
"""

if __name__ == "__main__":

    if len(sys.argv) > 2:
        conn_string = sys.argv[1].strip()
        rel_file_path = sys.argv[2].strip()
    else:
        conn_string = sys.argv[0].strip()
        rel_file_path = sys.argv[1].strip()

    data = {}

    data["IsEncrypted"] = "false"
    data["Values"] = {
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsStorage": conn_string,
        "EC_EMAIL": os.environ["EC_EMAIL"],
        "EC_PASSWORD": os.environ["EC_PASSWORD"],
        "EC_VERBOSE_LEVEL": os.environ["EC_VERBOSE_LEVEL"],
        "EC_DEFAULT_OUTPUT": os.environ["EC_DEFAULT_OUTPUT"],
        "EC_HIDE": os.environ["EC_HIDE"],
        "EC_MFA": os.environ["EC_MFA"],
    }

    with open(rel_file_path, 'w') as outfile:
        json.dump(data, outfile)
