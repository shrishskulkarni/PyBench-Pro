import cProfile
import io
import pstats

from .sandbox import restricted_globals, run_worker


def _profile_worker(code, n, queue):
    namespace = {}
    try:
        compiled = compile(code, "<user_code>", "exec")
        globals_dict = restricted_globals()
        exec(compiled, globals_dict, namespace)
        func = namespace.get("test_function")
        if not callable(func):
            queue.put({"error": "Function test_function(n) not found"})
            return
        profiler = cProfile.Profile()
        profiler.enable()
        func(n)
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)
        text = stream.getvalue()
        total_calls = stats.total_calls
        total_time = stats.total_tt
        lines = [line for line in text.splitlines() if line.strip()]
        header_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("ncalls"):
                header_index = i
                break
        top_lines = lines[header_index : header_index + 12]
        queue.put(
            {
                "total_calls": total_calls,
                "total_time": total_time,
                "top_lines": top_lines,
            }
        )
    except Exception as exc:
        queue.put({"error": str(exc)})


def analyze_profile(code, n=10000, timeout=3.0):
    result = run_worker(_profile_worker, (code, n), timeout)
    if "error" in result:
        return result
    return {
        "total_calls": result.get("total_calls", 0),
        "total_time": result.get("total_time", 0.0),
        "top_lines": result.get("top_lines", []),
    }

