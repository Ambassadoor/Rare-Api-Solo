class User:
    def __init__(
            self,
            id,
            first_name,
            last_name,
            email,
            bio,
            username,
            created_on,
            active,
            is_admin,
            profile_image_url,
            updated_at,
            password=None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.bio = bio
        self.username = username
        self.password = password
        self.created_on = created_on
        self.active = active
        self.is_admin = is_admin
        self.profile_image_url = profile_image_url
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "bio": self.bio,
            "username": self.username,
            "created_on": self.created_on,
            "active": self.active,
            "is_admin": self.is_admin,
            "profile_image_url": self.profile_image_url,
            "updated_at": self.updated_at,
        }