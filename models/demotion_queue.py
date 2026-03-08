class DemotionQueue:
    def __init__(self, action, admin_id, approver_one_id):
        self.action = action
        self.admin_id = admin_id
        self.approver_one_id = approver_one_id

    def to_dict(self):
        return {
            "action": self.action,
            "admin_id": self.admin_id,
            "approver_one_id": self.approver_one_id,
        }
