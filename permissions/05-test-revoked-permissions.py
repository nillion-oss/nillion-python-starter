from pdb import set_trace as bp
import argparse
import asyncio
import py_nillion_client as nillion
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getUserKeyFromFile, getNodeKeyFromFile

load_dotenv()

parser = argparse.ArgumentParser(
    description="Check that retrieval permissions on a Secret have been revoked"
)
parser.add_argument(
    "--store_id",
    required=True,
    type=str,
    help="Store ID from the writer client store operation",
)
args = parser.parse_args()


async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    userkey = getUserKeyFromFile(os.getenv("NILLION_USERKEY_PATH_PARTY_1"))
    nodekey = getNodeKeyFromFile(os.getenv("NILLION_NODEKEY_PATH_PARTY_1"))
    
    # Reader Nillion client
    reader = create_nillion_client(userkey, nodekey)
    reader_user_id = reader.user_id()

    try:
        secret_name = "my_int1"
        result = await reader.retrieve_secret(cluster_id, args.store_id, secret_name)
        print(f"⛔ FAIL: {reader_user_id} user id with revoked permissions was allowed to access secret", file=sys.stderr)
    except TypeError as e:
        if str(e) == "the user is not authorized to access the secret":
            print(f"🦄 Success: After user permissions were revoked, {reader_user_id} was not allowed to access secret", file=sys.stderr)
            pass
        else:
            raise(e)


asyncio.run(main())
