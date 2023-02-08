import requests
import yaml
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def check_external_septic_info(address, zipcode):
    """
    Consults external property service to determine whether the
    specified property has a septic system

    Args:
        address (str): The street address of the property
        zipcode (str): The zipcode of the property

    Returns:
        str: Value of this property's septic status, either 'septic',
        'not septic', or 'unknown'
    """

    conf_file = getattr(settings, 'EXTERNAL_PROPERTY_INFO_SERVICE_CONFIG')
    with open(conf_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    if not config:
        raise ValueError("Problem loading config for external property info service")

    property_info = get_external_property_info(address, zipcode, config)
    if property_info:
        # Find the potentially nested value for the property's use of septic
        septic_key = config['SEPTIC_KEY']
        while '/' in septic_key:
            parent_key, septic_key = septic_key.split('/', 1)
            property_info = property_info[parent_key]

        sewer_type = property_info[septic_key].lower()
        logger.info("-----Sewer type '{}' found at address '{}, {}'-----".format(sewer_type, address, zipcode))
        return 'septic' if sewer_type == config['SEPTIC_VALUE'].lower() else "not septic"
    return 'unknown'


def get_external_property_info(address, zipcode, external_api_config):
    """
    Fetches supplemental property information from an external service

    Args:
        address (str): The street address of the property
        zipcode (str): The zipcode of the property
        external_api_config (dict): Configured values for the external service

    Returns:
        dict: Property data from the external service
    """
    external_url = external_api_config['URL']
    auth_header = {
        'Authorization': 'Bearer {}'.format(external_api_config['AUTH_TOKEN'])
    }
    params = {
        'address': address,
        'zipcode': zipcode,
    }
    try:
        response = requests.get(
            external_url,
            params=params,
            headers=auth_header,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error('Problem communicating with external API: {}'.format(str(e)))
        raise
