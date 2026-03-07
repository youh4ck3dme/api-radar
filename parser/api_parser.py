import re

def parse_nginx_log_line(line):
    """
    Parses a single line of Nginx access log to extract method and endpoint.
    Example: 88.212.19.47 - - [08/Mar/2026:00:07:21 +0100] "GET /api/users HTTP/1.1" 200
    Returns: (Method, Endpoint) e.g., ("GET", "/api/users")
    """
    # Regex to capture the method and the URL path from the request string
    # Matches "METHOD /PATH HTTP/..."
    match = re.search(r'"([A-Z]+)\s+([^\s?]+)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None
