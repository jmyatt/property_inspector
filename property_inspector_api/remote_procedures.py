from modernrpc.core import rpc_method, Protocol
from modernrpc.auth.basic import http_basic_auth_login_required

from .utils import check_external_septic_info


@rpc_method(protocol=Protocol.JSON_RPC)
@http_basic_auth_login_required
def check_has_septic(address, zipcode):
    """
    Determines whether the specified property has a septic water system.

    Args:
        address (str): The street address of the property
        zipcode (str): The zipcode of the property

    Returns:
        str: The property's septic status, either 'septic', 'not septic',
        or 'unknown'
    """
    return check_external_septic_info(address, zipcode)
