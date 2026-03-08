class Session:
    def __init__(self, id, token, user_id, created_at, last_seen_at):
        self.id = id
        self.token = token
        self.user_id = user_id
        self.created_at = created_at
        self.last_seen_at = last_seen_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_seen_at": self.last_seen_at
        }
