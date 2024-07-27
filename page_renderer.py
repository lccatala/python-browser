class PageRenderer:
    def __init__(self, html: str, extra_entities: dict[str, str] = {}) -> None:
        self.html = html

        self.entities = {
            "&lt;": "<",
            "&bt;": ">"
        } 
        if len(extra_entities) > 0:
            self.entities = dict(self.entities, **extra_entities)

    def _handle_possible_entity(self, i: int):
        c = self.html[i]
        for k in self.entities:
            if i < (len(self.html) - len(k)):
                if self.html[i:i+len(k)] == k:
                    self._in_entity_count = len(k)
                    c = self.entities[k]
        return c

    def show(self, view_source: bool=False) -> None:
        if view_source:
            print(self.html)
            return

        self._in_entity_count = 0
        in_tag = False
        for i, c in enumerate(self.html):
            if self._in_entity_count > 0:
                self._in_entity_count -= 1
                continue

            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                if c == "&":
                    c = self._handle_possible_entity(i)
                print(c, end="")
