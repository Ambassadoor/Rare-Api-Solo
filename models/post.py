class Post:
    def __init__(
            self,
            id,
            user_id,
            category_id,
            title,
            publication_date,
            content,
            status,
            submitted_at,
            reviewed_at,
            reviewer_id,
            admin_comments,
            updated_at,
            image_url,
            created_on,
    ):
        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.title = title
        self.publication_date = publication_date
        self.content = content
        self.status = status
        self.submitted_at = submitted_at
        self.reviewed_at = reviewed_at
        self.reviewer_id = reviewer_id
        self.admin_comments = admin_comments
        self.updated_at = updated_at
        self.image_url = image_url
        self.created_on = created_on

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "title": self.title,
            "publication_date": self.publication_date,
            "content": self.content,
            "status": self.status,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "reviewer_id": self.reviewer_id,
            "admin_comments": self.admin_comments,
            "updated_at": self.updated_at,
            "image_url": self.image_url,
            "created_on": self.created_on,
        }