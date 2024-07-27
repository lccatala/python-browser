from url import URL

entities = {
    "&lt;": "<",
    "&bt;": ">"
}

def handle_possible_entity(body: str, i: int):
    in_entity_count = 0
    c = body[i]
    for k in entities:
        if i < (len(body) - len(k)):
            if body[i:i+len(k)] == k:
                in_entity_count = len(k)
                c = entities[k]
    return in_entity_count, c

def show(body: str) -> None:
    in_tag = False
    in_entity_count = 0
    for i, c in enumerate(body):
        if in_entity_count > 0:
            in_entity_count -= 1
            continue

        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            if c == "&":
                in_entity_count, c = handle_possible_entity(body, i)
            print(c, end="")

def load(url: URL) -> None:
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys

    start_url = "file://start.html"
    if len(sys.argv) >= 2:
        start_url = sys.argv[1]

    load(URL(start_url))
