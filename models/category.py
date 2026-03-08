class Category:
    def __init__(
            self,
            id,
            label
    ):
        self.id = id
        self.label = label

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label
        }