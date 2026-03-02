from flask import Flask, render_template, request
from analyzer.runtime import analyze_runtime
from analyzer.memory import analyze_memory
from analyzer.complexity import analyze_scalability
from analyzer.profiler import analyze_profile
from analyzer.static_analysis import analyze_code


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    analysis = {}
    errors = []
    if request.method == "POST":
        code = request.form.get("code", "")
        if not code.strip():
            errors.append("Please provide Python code defining test_function(n).")
        else:
            static_result = analyze_code(code)
            if "error" in static_result:
                errors.append(static_result["error"])
            else:
                analysis["static"] = static_result
                runtime_result = analyze_runtime(code)
                if "error" in runtime_result:
                    errors.append(runtime_result["error"])
                else:
                    analysis["runtime"] = runtime_result
                memory_result = analyze_memory(code)
                if "error" in memory_result:
                    errors.append(memory_result["error"])
                else:
                    analysis["memory"] = memory_result
                scalability_result = analyze_scalability(code)
                if "error" in scalability_result:
                    errors.append(scalability_result["error"])
                else:
                    analysis["complexity"] = scalability_result
                profile_result = analyze_profile(code)
                if "error" in profile_result:
                    errors.append(profile_result["error"])
                else:
                    analysis["profile"] = profile_result
    return render_template("index.html", code=code, analysis=analysis, errors=errors)


if __name__ == "__main__":
    app.run(debug=True)

