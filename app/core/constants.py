from gzip import READ
from tkinter import PROJECTING
from typing import List


# class Constants:
#     ACCESS_DIRECTOR_SLUG = "access-director"
#     BUSINESS_STATUS = {
#         "PENDING_APPROVAL": 1,
#         "ACTIVE": 2,
#         "SUSPEND": 3,
#         "INACTIVE": 4,
#         "DEACTIVATED": 5,
#     }
#     DESIGNER_SLUG = "designer"


# constants = Constants()

class RoleKey:
    ADMIN = "admin"
    OWNER = "owner"
    CUSTOMER = "customer"

role_key = RoleKey()


class ResourceType:
    FARM = "farm"
    TREE = "tree"
    PRODUCT = "product"
    FERTILIZER = "fertilizer"

    def get_list_types(self) -> List[str]:
        return [self.FARM, self.TREE, self.FERTILIZER, self.PRODUCT]
    
resource_type = ResourceType()


class RfidType:
    FARM = "farm"
    TREE = "tree"
    PRODUCT = "product"
    FERTILIZER = "fertilizer"
    
rfid_type = RfidType()


class TransferStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"

transfer_status = TransferStatus()

class ProductStatus:
    NORMAL = "normal"
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"

product_transfer_status = ProductStatus()


class RoleAuthentication:
    roles_all = [role_key.ADMIN, role_key.OWNER, role_key.CUSTOMER]
    roles_admin = [role_key.ADMIN]
    roles_customer = [role_key.ADMIN, role_key.CUSTOMER]
    roles_owner = [role_key.ADMIN, role_key.OWNER]
    
role_authen = RoleAuthentication()
