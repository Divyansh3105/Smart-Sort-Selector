from flask import Flask, render_template, request
import time

app = Flask(__name__)

# Sorting algorithms (dummy implementations)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result += left[i:]
    result += right[j:]
    return result

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)

def heap_sort(arr):
    import heapq
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]

def counting_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    min_val = min(arr)
    range_of_elements = max_val - min_val + 1
    count = [0] * range_of_elements
    output = [0] * len(arr)
    for num in arr:
        count[num - min_val] += 1
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    for num in reversed(arr):
        output[count[num - min_val] - 1] = num
        count[num - min_val] -= 1
    return output

# Recommendation logic
def analyze_and_recommend(data):
    n = len(data)
    is_sorted = data == sorted(data)
    is_reversed = data == sorted(data, reverse=True)
    has_duplicates = len(set(data)) != n

    if n <= 10:
        return "Insertion Sort", "Small dataset; insertion sort is efficient.", "Best: O(n), Avg/Worst: O(n²)"
    elif is_sorted:
        return "Insertion Sort", "Already sorted; insertion sort performs best.", "Best: O(n), Avg/Worst: O(n²)"
    elif is_reversed and not has_duplicates:
        return "Quick Sort", "Reverse sorted without duplicates; quick sort is efficient.", "Best: O(n log n), Worst: O(n²)"
    elif all(x >= 0 for x in data) and has_duplicates:
        return "Counting Sort", "Non-negative integers with duplicates; counting sort is ideal.", "O(n + k), where k = max value"
    else:
        return "Merge Sort", "Large or random data; merge sort offers guaranteed performance.", "O(n log n)"

# Run a sort and measure time
def run_sort(data, algo_name):
    start = time.perf_counter()
    if algo_name == "Bubble Sort":
        sorted_data = bubble_sort(data.copy())
    elif algo_name == "Insertion Sort":
        sorted_data = insertion_sort(data.copy())
    elif algo_name == "Merge Sort":
        sorted_data = merge_sort(data.copy())
    elif algo_name == "Quick Sort":
        sorted_data = quick_sort(data.copy())
    elif algo_name == "Heap Sort":
        sorted_data = heap_sort(data.copy())
    elif algo_name == "Counting Sort":
        sorted_data = counting_sort(data.copy())
    else:
        return [], 0
    end = time.perf_counter()
    return sorted_data, end - start

# Benchmark all algorithms
def benchmark_all_sorts(data):
    algorithms = [
        "Bubble Sort",
        "Insertion Sort",
        "Merge Sort",
        "Quick Sort",
        "Heap Sort",
        "Counting Sort"
    ]
    results = {}
    for algo in algorithms:
        try:
            _, time_taken = run_sort(data.copy(), algo)
            results[algo] = time_taken
        except Exception:
            results[algo] = None
    return results

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "data": [],
        "analysis": {},
        "recommended": None,
        "reason": "",
        "complexity": "",
        "sorted_data": [],
        "time_taken": None,
        "benchmark": {}
    }

    if request.method == "POST":
        raw = request.form.get("dataset")
        if raw:
            try:
                data = [int(x.strip()) for x in raw.strip().split(',') if x.strip()]
                context["data"] = data

                # Analyze and recommend
                algo, reason, complexity = analyze_and_recommend(data)
                context["recommended"] = algo
                context["reason"] = reason
                context["complexity"] = complexity
                context["analysis"] = {
                    "size": len(data),
                    "order": "sorted" if data == sorted(data) else "reversed" if data == sorted(data, reverse=True) else "random",
                    "duplicates": len(set(data)) != len(data)
                }

                # Run sort
                if "run_sort" in request.form:
                    algo_choice = request.form.get("algo_choice")
                    sorted_data, time_taken = run_sort(data, algo_choice)
                    context["sorted_data"] = sorted_data
                    context["time_taken"] = f"{time_taken:.5f}"

                # Benchmark
                if "benchmark" in request.form:
                    context["benchmark"] = benchmark_all_sorts(data)

            except ValueError as ve:
                context["error"] = f"Invalid input! Ensure all entries are integers. Error: {ve}"

    return render_template("index.html", **context)

if __name__ == "__main__":
    app.run(debug=True)
