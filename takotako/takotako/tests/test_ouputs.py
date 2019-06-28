import json

# SHOW INT DESCRIPTION outputs
with open("takotako/tests/outputs/output_show_int_description.txt", "r") as f:
    output_description = f.read()
with open("takotako/tests/outputs/output_show_int_description_processed.json", "r") as f:
    output_description_processed = json.load(f)
# SHOW INT STATUS outputs
with open("takotako/tests/outputs/output_show_int_status.txt", "r") as f:
    output_status = f.read()
with open("takotako/tests/outputs/output_show_int_status_processed.json", "r") as f:
    output_status_processed = json.load(f)
# SHOW RUN | S INTERFACE outputs
with open("takotako/tests/outputs/output_show_run_all_int.txt", "r") as f:
    output_run_all_int = f.read()
with open("takotako/tests/outputs/output_show_run_all_int_processed.json", "r") as f:
    output_run_all_int_processed = json.load(f)
# SHOW MAC ADDRESS-TABLE
with open("takotako/tests/outputs/output_show_mac_address.txt", "r") as f:
    output_mac_address = f.read()
with open("takotako/tests/outputs/output_show_mac_address_processed.json", "r") as f:
    output_mac_address_processed = json.load(f)
# SHOW CPD NEIGHBORS
with open("takotako/tests/outputs/output_show_cdp_neighbors.txt", "r") as f:
    output_cdp_neighbors = f.read()
with open("takotako/tests/outputs/output_show_cdp_neighbors_processed.json", "r") as f:
    output_cdp_neighbors_processed = json.load(f)