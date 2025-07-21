from log_manipulation.log import log

def manipulate_logs(log_data,print_interval = 50,debug = False):
    # Set option to stop thousands of warnings 
    # pd.set_option('future.no_silent_downcasting', True)

    # # Grab the class object from the log_manipulation folder
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log_manipulation')))

    # from log import log # type: ignore

    # Import RGL Logs

    clean_log_data = {}
    error_logs = {}

    ids = log_data.keys()
    count = 0
    for i,id in enumerate(ids):
        count += 1
        match = log_data[id]

        # Print The Progress
        if count == print_interval:
            count = 0
            print(f'Manipulated {i} / {len(log_data)} Log Data')

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

    return clean_log_data,error_logs

