import tracemalloc

from .sandbox import restricted_globals, run_worker


def _memory_worker(code, n, repeats, queue):
    namespace = {}
    try:
        compiled = compile(code, "<user_code>", "exec")
        globals_dict = restricted_globals()
        exec(compiled, globals_dict, namespace)
        func = namespace.get("test_function")
        if not callable(func):
            queue.put({"error": "Function test_function(n) not found"})
            return
        tracemalloc.start()
        current_samples = []
        peak_samples = []
        for _ in range(repeats):
            func(n)
            current, peak = tracemalloc.get_traced_memory()
            current_samples.append(current)
            peak_samples.append(peak)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        queue.put(
            {
                "current_samples": current_samples,
                "peak_samples": peak_samples,
                "final_current": current,
                "final_peak": peak,
            }
        )
    except Exception as exc:
        queue.put({"error": str(exc)})


def analyze_memory(code, n=10000, repeats=5, timeout=2.0):
    result = run_worker(_memory_worker, (code, n, repeats), timeout)
    if "error" in result:
        return result
    current_samples = result.get("current_samples") or []
    peak_samples = result.get("peak_samples") or []
    if not peak_samples:
        return {"error": "No memory data collected"}
    peak_memory = max(peak_samples)
    average_memory = sum(current_samples) / len(current_samples) if current_samples else 0.0
    growth = 0.0
    if len(current_samples) > 1:
        growth = current_samples[-1] - current_samples[0]
    return {
        "n": n,
        "runs": repeats,
        "peak_memory": peak_memory,
        "average_memory": average_memory,
        "memory_growth": growth,
        "current_samples": current_samples,
        "peak_samples": peak_samples,
    }

