import multiprocessing as mp


SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "sorted": sorted,
    "any": any,
    "all": all,
    "print": print,
}


def restricted_globals():
    return {"__builtins__": SAFE_BUILTINS.copy()}


def run_worker(target, args, timeout):
    queue = mp.Queue()
    process = mp.Process(target=target, args=(*args, queue))
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        return {"error": "Execution timed out"}
    if queue.empty():
        return {"error": "No result from worker"}
    return queue.get()

