import re
import chardet

def parse_logs(file):
    logs = []
    # Debug: Print file details
    print(f"File object: {file}")
    print(f"File name: {file.filename}")

    # Reset file pointer
    file.seek(0)
    raw_content = file.read()
    print(f"Raw bytes: {len(raw_content)} bytes")

    # Detect encoding
    if raw_content:
        detected = chardet.detect(raw_content)
        print(f"Detected encoding: {detected}")
        encoding = detected['encoding'] or 'utf-8'
    else:
        print("No content in file")
        encoding = 'utf-8'

    # Decode content
    try:
        content = raw_content.decode(encoding).splitlines()
        print(f"Decoded content with {encoding}: {content[:5]}... (first 5 lines)")
    except Exception as e:
        print(f"Decode error with {encoding}: {str(e)}")
        content = raw_content.decode('utf-8', errors='ignore').splitlines()
        print(f"Content with errors ignored: {content[:5]}... (first 5 lines)")

    # Regex patterns for different log formats
    standard_pattern = re.compile(r'^\[(\d+)\]\s+(\S+)\s+(\[.*?\])\s*[-]+\s*(.+)$')  # [thread] timestamp [category] - message
    continuation_pattern = re.compile(r'^\[(\d+)\]\s+(\S+)\s+(\[.*?\])\s*[|+]\s*(.+)$')  # [thread] timestamp [category] |/+ message
    xml_pattern = re.compile(r'^<[^>]+>.*</[^>]+>$|^<[^>]+/>$')  # <tag>...</tag> or <tag/>

    for line in content:
        line = line.strip()
        if not line:
            print(f"Skipping empty line")
            continue

        # Try standard format
        standard_match = standard_pattern.match(line)
        if standard_match:
            thread_id, timestamp, category, message = standard_match.groups()
            log_entry = {
                'timestamp': timestamp,
                'level': category.strip('[]'),
                'message': message
            }
            logs.append(log_entry)
            print(f"Parsed standard log: {log_entry}")
            continue

        # Try continuation or code reference format
        cont_match = continuation_pattern.match(line)
        if cont_match:
            thread_id, timestamp, category, message = cont_match.groups()
            log_entry = {
                'timestamp': timestamp,
                'level': category.strip('[]'),
                'message': message
            }
            logs.append(log_entry)
            print(f"Parsed continuation log: {log_entry}")
            continue

        # Check for XML
        if xml_pattern.match(line):
            log_entry = {
                'timestamp': '',
                'level': 'XML',
                'message': line
            }
            logs.append(log_entry)
            print(f"Parsed XML log: {log_entry}")
            continue

        # Fallback: treat as raw message
        print(f"Failed to match any pattern for line: {line}")
        log_entry = {
            'timestamp': '',
            'level': 'UNKNOWN',
            'message': line
        }
        logs.append(log_entry)
        print(f"Fallback log: {log_entry}")

    print(f"Final logs list length: {len(logs)}")
    return logs