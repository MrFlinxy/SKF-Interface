from pathlib import Path
from datetime import datetime


def get_file_sizes(directory):
    result = []
    path = Path(directory)
    files = path.iterdir()
    for file in files:
        size_bytes = file.stat().st_size
        if size_bytes >= 0 and size_bytes < 1000:
            nilai = size_bytes
            size = f"{str(nilai)[:5]} B"
        elif size_bytes > 1e3 and size_bytes < 1e6:
            nilai = size_bytes / 1e3
            size = f"{str(nilai)[:5]} KB"
        elif size_bytes > 1e6 and size_bytes < 1e9:
            nilai = size_bytes / 1e6
            size = f"{str(nilai)[:5]} MB"
        elif size_bytes > 1e9:
            nilai = size_bytes / 1e9
            size = f"{str(nilai)[:4]} GB"
        date = datetime.fromtimestamp(file.stat().st_ctime).strftime(
            "%d-%m-%Y %H:%M:%S"
        )
        result.append({"fname": file.name, "size": size, "date": date})
    return result
