class ProcessPool:
    def __init__(self, procs_list = []):
        # make global list of processes to ba accessed
        global procs
        global finished_count
        global size
        size = len(procs_list)
        if len(procs_list):
            procs = procs_list
        finished_count = 0

    def acc_finish(self):
        finished_count += 1

    def get_finished_count(self) -> int:
        return finished_count

    def get_size(self) -> int:
        return size

