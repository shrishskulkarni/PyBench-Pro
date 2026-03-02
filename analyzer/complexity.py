import base64
import io
import math
import time

from .sandbox import restricted_globals, run_worker


SCALES = [1000, 5000, 10000, 20000]


def _scalability_worker(code, sizes, queue):
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
        for n in sizes:
            start = time.perf_counter()
            func(n)
            end = time.perf_counter()
            times.append(end - start)
        queue.put({"sizes": sizes, "times": times})
    except Exception as exc:
        queue.put({"error": str(exc)})


def _estimate_complexity(sizes, times):
    if len(sizes) != len(times) or len(sizes) < 2:
        return "Unknown"
    ratios = []
    for i in range(1, len(sizes)):
        if times[i - 1] == 0:
            continue
        ratios.append(times[i] / times[i - 1])
    if not ratios:
        return "O(1)"
    avg_ratio = sum(ratios) / len(ratios)
    n_ratios = [sizes[i] / sizes[i - 1] for i in range(1, len(sizes))]
    avg_n_ratio = sum(n_ratios) / len(n_ratios)
    if avg_ratio < 1.5:
        return "O(1)"
    if abs(avg_ratio - avg_n_ratio) / avg_n_ratio < 0.5:
        return "O(n)"
    log_ratios = []
    for i in range(1, len(sizes)):
        prev = sizes[i - 1]
        curr = sizes[i]
        if prev <= 0 or curr <= 0:
            continue
        log_ratio = (curr * math.log2(curr)) / (prev * math.log2(prev))
        log_ratios.append(log_ratio)
    if log_ratios:
        avg_log_ratio = sum(log_ratios) / len(log_ratios)
        if abs(avg_ratio - avg_log_ratio) / avg_log_ratio < 0.5:
            return "O(n log n)"
    if avg_ratio > avg_n_ratio * 1.2:
        return "O(n^2)"
    return "Unknown"


def _build_svg(sizes, times):
    if not sizes or not times or max(times) == 0:
        width = 400
        height = 220
        svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#111827"/><text x="50%" y="50%" text-anchor="middle" fill="#9CA3AF" font-size="14">No runtime data</text></svg>'
        return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode(
            "ascii"
        )
    width = 400
    height = 220
    padding = 40
    max_time = max(times)
    min_time = min(times)
    time_span = max_time - min_time or max_time or 1.0
    x_min = min(sizes)
    x_max = max(sizes)
    x_span = x_max - x_min or 1.0
    points = []
    for n, t in zip(sizes, times):
        x = padding + (n - x_min) / x_span * (width - 2 * padding)
        y = height - padding - (t - min_time) / time_span * (height - 2 * padding)
        points.append(f"{x},{y}")
    path = " ".join(points)
    labels = []
    for n, t in zip(sizes, times):
        x = padding + (n - x_min) / x_span * (width - 2 * padding)
        y = height - padding - (t - min_time) / time_span * (height - 2 * padding)
        labels.append(
            f'<circle cx="{x}" cy="{y}" r="3" fill="#60A5FA"/><text x="{x}" y="{y - 8}" fill="#9CA3AF" font-size="10">{t:.4f}s</text>'
        )
    svg = io.StringIO()
    svg.write(
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
    )
    svg.write('<rect width="100%" height="100%" fill="#020617"/>')
    svg.write(
        f'<polyline fill="none" stroke="#3B82F6" stroke-width="2" points="{path}"/>'
    )
    for label in labels:
        svg.write(label)
    svg.write(
        f'<text x="{padding}" y="{height - padding + 20}" fill="#9CA3AF" font-size="11">Input size n</text>'
    )
    svg.write(
        f'<text x="{padding}" y="{padding - 15}" fill="#9CA3AF" font-size="11">Runtime (seconds)</text>'
    )
    svg.write("</svg>")
    encoded = base64.b64encode(svg.getvalue().encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + encoded


def analyze_scalability(code, timeout=4.0):
    sizes = list(SCALES)
    result = run_worker(_scalability_worker, (code, sizes), timeout)
    if "error" in result:
        return result
    times = result.get("times") or []
    if not times:
        return {"error": "No scalability data collected"}
    complexity = _estimate_complexity(sizes, times)
    graph_data_uri = _build_svg(sizes, times)
    return {
        "sizes": sizes,
        "times": times,
        "complexity": complexity,
        "graph_data_uri": graph_data_uri,
    }

