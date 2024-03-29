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
    description="Use read permissions to retrieve a secret owned by another user on the Nillion network"
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

    secret_name = "my_int1"

    # Reader retrieves the named secret by store id
    print(f"Retrieving secret as reader: {reader_user_id}")
    result = await reader.retrieve_secret(cluster_id, args.store_id, secret_name)

    print(f"🦄 Retrieved {secret_name} secret, value = {result[1].value}", file=sys.stderr)
    print("\n\nRun the following command to revoke the reader's retrieve permissions to the secret")
    print(f"\n📋 python3 04-revoke-read-permissions.py --store_id {args.store_id} --revoked_user_id {reader_user_id}")


asyncio.run(main())
