import statistics
import time

from .sandbox import restricted_globals, run_worker


def _runtime_worker(code, n, repeats, queue):
    data = {}
    namespace = {}
    try:
        compiled = compile(code, "<user_code>", "exec")
        globals_dict = restricted_globals()
        exec(compiled, globals_dict, namespace)
        func = namespace.get("test_function")
        if not callable(func):
            queue.put({"error": "Function test_function(n) not found"})
            return
        times = []
        for _ in range(repeats):
            start = time.perf_counter()
            func(n)
            end = time.perf_counter()
            times.append(end - start)
        data["times"] = times
        queue.put(data)
    except Exception as exc:
        queue.put({"error": str(exc)})


def analyze_runtime(code, n=10000, repeats=5, timeout=2.0):
    result = run_worker(_runtime_worker, (code, n, repeats), timeout)
    if "error" in result:
        return result
    times = result.get("times") or []
    if not times:
        return {"error": "No timing data collected"}
    avg = statistics.mean(times)
    minimum = min(times)
    maximum = max(times)
    stddev = statistics.pstdev(times) if len(times) > 1 else 0.0
    throughput = 1.0 / avg if avg > 0 else 0.0
    return {
        "n": n,
        "runs": repeats,
        "times": times,
        "average": avg,
        "min": minimum,
        "max": maximum,
        "stddev": stddev,
        "throughput": throughput,
    }

