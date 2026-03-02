# PyBench Pro

PyBench Pro is a full‑stack Python web app built with Flask that lets you paste a Python function `test_function(n)` and run a complete analysis in one place.

It focuses on:

- **Runtime analysis** (timings and throughput)
- **Memory usage** (via `tracemalloc`)
- **Scalability / complexity** (multiple input sizes + complexity guess)
- **CPU profiling** (via `cProfile`)
- **Static code metrics** (AST‑based, cyclomatic complexity, recursion, globals)

---

## Features

- **Runtime analysis**
  - Runs `test_function(n)` 5 times with `time.perf_counter()`
  - Reports average, min, max, standard deviation, and throughput (ops/s)

- **Memory analysis**
  - Uses `tracemalloc` to track memory
  - Shows peak memory, average memory, and memory growth between runs

- **Scalability / complexity**
  - Benchmarks input sizes: `n = 1000, 5000, 10000, 20000`
  - Estimates complexity among `O(1)`, `O(n)`, `O(n log n)`, `O(n^2)`, or `Unknown`
  - Renders a runtime growth graph (SVG) directly in the dashboard

- **CPU profiling**
  - Uses `cProfile` + `pstats`
  - Shows total calls, total execution time, and the top slowest functions

- **Static code analysis**
  - Parses code with `ast`
  - Counts lines, loops, conditionals, function definitions
  - Estimates cyclomatic complexity
  - Detects recursion, nested loop depth, and global variable usage

- **Safety**
  - Executes user code in a separate process with timeouts
  - Restricted builtins (simple sandbox)
  - Handles syntax errors and runtime errors gracefully

---

## Project structure

```text
pybench-pro/
├── app.py
├── analyzer/
│   ├── runtime.py
│   ├── memory.py
│   ├── complexity.py
│   ├── profiler.py
│   ├── static_analysis.py
│   └── sandbox.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── requirements.txt
```

---

## Running locally

1. **Clone the repository**

```bash
git clone https://github.com/shrishskulkarni/PyBench-Pro.git
cd PyBench-Pro
```

2. **(Optional) Create and activate a virtual environment**

```bash
python -m venv .venv

# PowerShell
.\.venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the Flask app**

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## Using the analyzer

In the main textarea, paste Python code that defines a function named `test_function(n)`. For example:

```python
def test_function(n):
    total = 0
    for i in range(n):
        total += i
    return total
```

Click **Analyze Code** to see:

- Overview summary
- Detailed runtime stats
- Memory behavior
- Complexity estimate and runtime graph
- CPU profile
- Static code metrics and quality signals

