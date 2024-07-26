from url import URL

def show(body: str) -> None:
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
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
