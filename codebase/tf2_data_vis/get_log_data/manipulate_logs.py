from ..log_manipulation.log import log
from .batch import save_batch

def manipulate_logs(log_data,
                    debug = False,
                    batch_size = 100,
                    output_dir = None,
                    parent_dir = None):

    # Import RGL Logs

    clean_log_data = {}
    error_logs = {}

    ids = log_data.keys()
    batch_counter = 1
    for i,id in enumerate(ids):
        match = log_data[id]

        # Print The Progress
        print(f'Manipulated {i+1} / {len(log_data)} Log Data')

        # Try to turn log data into clean log class object
        # If successful, add to rgl_data list
        try:
            make_log = log(log = match,id = id,debug = debug)
            clean_log_data[id] = make_log
        # Errors are added to the error_data list
        except Exception as e:
            print(f"Skipping index {i} due to error: {e}")
            error_logs[id] = match
            continue

        # Save batches
        if i % batch_size == 0 or i == len(log_data) or i == len(log_data) -1 or i == len(log_data) + 1:
            save_batch(batch = batch_counter,
                       batch_type = "clean_log_data",
                       parent_dir = parent_dir,
                       output_dir=output_dir,
                       object = clean_log_data
                       )
            save_batch(batch = batch_counter,
                       batch_type = "error_logs",
                       parent_dir = parent_dir,
                       output_dir=output_dir,
                       object = error_logs
                       )
            batch_counter += 1
            clean_log_data = {}     
            error_logs = {}

    return

