import re


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

# Pattern of a string with SRT timecodes (00:00:00,000 --> 00:00:02,000)
SRT_TIMESTAMP = re.compile(r"^(\d{2}:\d{2}:\d{2})[,.]\d{3}\s*-->\s*(\d{2}:\d{2}:\d{2})[,.]\d{3}")


def _clean_error_message(msg: str) -> str:
    return _ANSI_ESCAPE.sub("", str(msg)).strip()

def srt_to_simple(content: str) -> str:
    lines = content.strip().replace("\r\n", "\n").split("\n")
    output: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.isdigit():
            i += 1
            if i >= len(lines):
                break
            ts_line = lines[i].strip()
            i += 1
            m = SRT_TIMESTAMP.match(ts_line)
            if m:
                start, end = m.group(1), m.group(2)
                text_parts: list[str] = []
                while i < len(lines) and lines[i].strip():
                    text_parts.append(lines[i].strip())
                    i += 1
                text = " ".join(text_parts)
                output.append(f"{start} - {end}: {text}")
        else:
            i += 1
    return "\n".join(output)


def srt_to_plain_text(content: str) -> str:
    lines = content.strip().replace("\r\n", "\n").split("\n")
    text_parts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if SRT_TIMESTAMP.match(line):
            continue
        text_parts.append(line)
    return "\n".join(text_parts)