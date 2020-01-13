def full_strip(value: str) -> str:
    """
    Strip every line.
    """

    text = []

    for line in value.splitlines():
        stripped_line = line.strip()

        if stripped_line:
            text.append(stripped_line)

    return "\n".join(text)
