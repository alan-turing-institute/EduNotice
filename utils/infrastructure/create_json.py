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
        "EC_MFA": os.environ["EC_MFA"],
        "ENS_SQL_HOST": os.environ["ENS_SQL_HOST"],
        "ENS_SQL_USER": os.environ["ENS_SQL_USER"],
        "ENS_SQL_PASS": os.environ["ENS_SQL_PASS"],
        "ENS_SQL_DBNAME": os.environ["ENS_SQL_DBNAME"],
        "ENS_SQL_PORT": os.environ["ENS_SQL_PORT"],
        "ENS_EMAIL_API": os.environ["ENS_EMAIL_API"],
        "ENS_FROM_EMAIL": os.environ["ENS_FROM_EMAIL"],
        "ENS_SUMMARY_RECIPIENTS": os.environ["ENS_SUMMARY_RECIPIENTS"],
        "ENS_EMAIL_EXCL": os.environ["ENS_EMAIL_EXCL"],
    }

    with open(rel_file_path, 'w') as outfile:
        json.dump(data, outfile)
