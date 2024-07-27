from url import URL
from page_renderer import PageRenderer


def load(url: URL) -> None:
    body = url.request()
    renderer = PageRenderer(body)
    view_source = url.scheme_prefix == "view-source"
    # renderer.show(view_source=view_source)


if __name__ == "__main__":
    import sys

    start_url = "file://start.html"
    if len(sys.argv) >= 2:
        start_url = sys.argv[1]

    load(URL(start_url))
