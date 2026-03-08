class Reaction:
    def __init__(self, id, label, emoji):
        self.id = id
        self.label = label
        self.emoji = emoji

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "emoji": self.emoji,
        }
