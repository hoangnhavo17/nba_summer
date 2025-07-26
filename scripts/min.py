def parse_min(min_str):
    if isinstance(min_str, str) and ":" in min_str:
        mins, secs = map(int, min_str.split(":"))
        return mins * 60 + secs
    try:
        return int(float(min_str) * 60)
    except:
        return 0.0
    
def format_sec(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

seconds = parse_min("12:34")
print(seconds)  # Output: 754
time_str = format_sec(seconds)
print(time_str)  # Output: "12:34"