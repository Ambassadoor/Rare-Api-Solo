class Comment:
    def __init__(
            self,
            id,
            post_id,
            author_id,
            content,
            subject
    ):
        self.id = id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.subject = subject

    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "content": self.content,
            "subject": self.subject,
        }