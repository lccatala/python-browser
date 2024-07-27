import sys
import socket
import ssl


class URL:
    def __init__(self, url: str) -> None:
        self.scheme_prefix = ""
        self.supported_schemes = [
            "http", 
            "view-source:http", 
            "https", 
            "view-source:https", 
            "file", 
            "view-source:file"
        ]
        if "://" in url:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in self.supported_schemes

            if ":" in self.scheme:
                self.scheme_prefix, self.scheme = self.scheme.split(":", 1)

            if self.scheme == "http":
                self.port = 80
                self._parse_http_url(url)
            elif self.scheme == "https":
                self.port = 443
                self._parse_http_url(url)
            elif self.scheme == "file":
                self._parse_file_url(url)
        elif ":" in url:
            self.scheme, url = url.split(":", 1)
            if self.scheme == "data":
                self._parse_data_url(url)

        self._socket = None


    def _parse_data_url(self, input_url: str) -> None:
        url_type, _ = input_url.split(",", 1)
        if url_type != "text/html":
            print(f"Unsupported data url type: {url_type}")
            exit()

        self.host = " ".join(sys.argv[1:])

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

    def _request_data(self) -> str:
        return self.host

    def _request_file(self) -> str:
        with open(self.host) as f:
            lines = "".join(f.readlines())
        return lines

    def request(self, extra_headers: dict[str, str]={}) -> str:
        if self.scheme == "file":
            return self._request_file()
        elif self.scheme == "data":
            return self._request_data()

        if self._socket is None:
            self._socket = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                self._socket = ctx.wrap_socket(self._socket, server_hostname=self.host)

        self._socket.connect((self.host, self.port))

        request =  f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        # request +=  "Connection: close\r\n"
        request +=  "User-Agent: lccatala\r\n"
        for h, v in extra_headers:
            request +=  f"{h}: {v}\r\n"
        request +=  "\r\n"
        self._socket.send(request.encode("utf8"))

        response = self._socket.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers: dict[str, str] = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        print(response_headers)

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Handle redirect
        if int(status) > 299 and int(status) < 400:
            self._socket.close()
            location = response_headers["location"]
            if location.startswith("/"):
                location = f"{self.scheme}://{self.host}/{location}"
            url = URL(location)
            return url.request()

        content_length = int(response_headers["content-length"])
        content = response.read(content_length)

        return content

