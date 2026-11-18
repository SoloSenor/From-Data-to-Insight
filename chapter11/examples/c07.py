def parse_count(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_count("12"))
print(parse_count("twelve"))
