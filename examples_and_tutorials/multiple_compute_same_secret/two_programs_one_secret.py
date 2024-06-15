"""
This example demonstrates how to compute multiple programs on the same secret
"""

import asyncio
import py_nillion_client as nillion
import os
import sys
import pytest

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getUserKeyFromFile, getNodeKeyFromFile

load_dotenv()

# Party 1 stores one secret and computes an addition and multiplcation program with it
async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    userkey = getUserKeyFromFile(os.getenv("NILLION_USERKEY_PATH_PARTY_1"))
    nodekey = getNodeKeyFromFile(os.getenv("NILLION_NODEKEY_PATH_PARTY_1"))
    client = create_nillion_client(userkey, nodekey)
    party_id = client.party_id
    user_id = client.user_id
    party_name = "Party1"

    # names and paths of the two programs we want to compute
    program_name_add = "addition_simple"
    program_mir_path_add = f"../../programs-compiled/{program_name_add}.nada.bin"

    program_name_mult = "multiplication_simple"
    program_mir_path_mult = f"../../programs-compiled/{program_name_mult}.nada.bin"

    # store program addition
    action_id_add = await client.store_program(
        cluster_id, program_name_add, program_mir_path_add
    )

    program_id_add = f"{user_id}/{program_name_add}"
    print('Stored program. action_id:', action_id_add)
    print('Stored program_id ad:', program_id_add)

    # store program multiplication
    action_id_mult = await client.store_program(
        cluster_id, program_name_mult, program_mir_path_mult
    )

    program_id_mult = f"{user_id}/{program_name_mult}"
    print('Stored program. action_id:', action_id_mult)
    print('Stored program_id for mult:', program_id_mult)

    # Create a secret - note both programs have the same input secret names
    stored_secret = nillion.Secrets({
        "my_int1": nillion.SecretInteger(500),
    })

    # we set the second secret to be inputted at computation time
    computation_time_secrets = nillion.Secrets({"my_int2": nillion.SecretInteger(10)})

    # define permissions - we do this as we only pass the compute bindings at compute time (not when storing the secret)
    permissions = nillion.Permissions.default_for_user(user_id)

    # Give compute permissions to the first party
    compute_permissions = {
        user_id: {program_id_mult, program_id_add},
    }

    permissions.add_compute_permissions(compute_permissions)

    # Store a secret
    store_id = await client.store_secrets(
        cluster_id, None, stored_secret, permissions
    )

    # check the permissions have been set correctly
    permissions_set = await client.retrieve_permissions(cluster_id, store_id)
    compute_allowed = permissions_set.is_compute_allowed(user_id, program_id_add)
    print(f"permissions: {compute_allowed}")


    # Compute the addition program
    compute_bindings = nillion.ProgramBindings(program_id_add)
    compute_bindings.add_input_party(party_name, party_id)
    compute_bindings.add_output_party(party_name, party_id)

    print(f"Computing using program {program_id_add}")
    print(f"Use secret store_id: {store_id}")

    # Compute on the secret
    compute_id = await client.compute(
        cluster_id,
        compute_bindings,
        [store_id],
        computation_time_secrets,
        nillion.PublicVariables({}),
    )

    # Print compute result
    print(f"The computation was sent to the network. compute_id: {compute_id}")
    while True:
        compute_event = await client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"✅  Compute complete for compute_id {compute_event.uuid}")
            print(f"🖥️  The result is {compute_event.result.value}")
            break

    # Compute the multiplication program
    compute_bindings = nillion.ProgramBindings(program_id_mult)
    compute_bindings.add_input_party(party_name, party_id)
    compute_bindings.add_output_party(party_name, party_id)

    print(f"Computing using program {program_id_mult}")
    print(f"Use secret store_id: {store_id}")

    # Compute on the secret
    compute_id = await client.compute(
        cluster_id,
        compute_bindings,
        [store_id],
        computation_time_secrets,
        nillion.PublicVariables({}),
    )

    # Print compute result
    print(f"The computation was sent to the network. compute_id: {compute_id}")
    while True:
        compute_event = await client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"✅  Compute complete for compute_id {compute_event.uuid}")
            print(f"🖥️  The result is {compute_event.result.value}")
            return compute_event.result.value


if __name__ == "__main__":
    asyncio.run(main())
