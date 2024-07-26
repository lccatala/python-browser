import socket
import ssl


class URL:
    def __init__(self, url: str) -> None:
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "http":
            self.port = 80
            self._parse_http_url(url)
        elif self.scheme == "https":
            self.port = 443
            self._parse_http_url(url)
        elif self.scheme == "file":
            self._parse_file_url(url)


    def _parse_file_url(self, input_url: str) -> None:
        self.host = input_url

    def _parse_http_url(self, input_url: str) -> None:
        if "/" not in input_url:
            input_url = input_url + "/"

        self.host, input_url = input_url.split("/", 1)
        self.path = "/" + input_url # The slash is part of the path

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request_file(self) -> str:
        with open(self.host) as f:
            lines = "".join(f.readlines())
        return lines

    def request(self, extra_headers: dict[str, str]={}) -> str:
        if self.scheme == "file":
            return self.request_file()

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        s.connect((self.host, self.port))

        request =  f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request +=  "Connection: close\r\n"
        request +=  "User-Agent: lccatala\r\n"
        for h, v in extra_headers:
            request +=  f"{h}: {v}\r\n"
        request +=  "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content

