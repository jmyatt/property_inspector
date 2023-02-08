import enum

from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch

from simplejson import loads


class RpcErrorCodes(enum.Enum):
    # https://www.jsonrpc.org/specification#error_object
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603


class PropertyInspectorTests(TestCase):
    test_username = 'testuser'
    test_password = 'hD*3lKe)@H$s'

    rpc_check_septic_method = 'check_has_septic'
    params_with_septic = ["123 main st", "94132"]
    params_without_septic = ["456 main st", "23149"]

    def setUp(self):
        test_user = User.objects.create_user(
            username=self.test_username,
            password=self.test_password
        )

    def send_post_request(
            self,
            include_login=True,
            method=None,
            params=None):

        if include_login:
            _ = self.client.login(username=self.test_username, password=self.test_password)

        rpc_method = method if method else self.rpc_check_septic_method
        rpc_params = params if isinstance(params, list) else self.params_with_septic

        return self.client.post(
            '/rpc/',
            data={"id": 1,
                  "jsonrpc": "2.0",
                  "method": rpc_method,
                  "params": rpc_params},
            content_type='application/json'
        )

    def test_rpc_doc_view_exists(self):
        response = self.client.get('/rpc-doc/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.rpc_check_septic_method, str(response.content))

    def test_rpc_endpoint_requires_post(self):
        response = self.client.get('/rpc/')
        self.assertEqual(response.status_code, 405)

        response = self.client.put('/rpc/')
        self.assertEqual(response.status_code, 405)

        response = self.client.patch('/rpc/')
        self.assertEqual(response.status_code, 405)

        response = self.client.delete('/rpc/')
        self.assertEqual(response.status_code, 405)

        response = self.client.post('/rpc/')
        self.assertEqual(response.status_code, 200)

    def test_septic_endpoint_not_authenticated(self):
        response = self.send_post_request(include_login=False)
        self.assertEqual(response.status_code, 200)

        content_dict = loads(response.content)
        self.assertIsNotNone(content_dict.get('error'))
        self.assertEqual(content_dict['error']['code'], RpcErrorCodes.InternalError.value)
        self.assertEqual(content_dict['error']['message'], 'Authentication failed when calling "check_has_septic"')

    def test_septic_endpoint_unknown_method(self):
        response = self.send_post_request(method='garbage_method')
        self.assertEqual(response.status_code, 200)

        content_dict = loads(response.content)
        self.assertIsNotNone(content_dict.get('error'))
        self.assertEqual(content_dict['error']['code'], RpcErrorCodes.MethodNotFound.value)
        self.assertEqual(content_dict['error']['message'], 'Method not found: "garbage_method"')

    def test_septic_endpoint_missing_params(self):
        response = self.send_post_request(params=[])
        self.assertEqual(response.status_code, 200)

        content_dict = loads(response.content)
        self.assertIsNotNone(content_dict.get('error'))
        self.assertEqual(content_dict['error']['code'], RpcErrorCodes.InvalidParams.value)
        self.assertIn(
            'Invalid parameters: check_has_septic() missing 2 required positional arguments',
            content_dict['error']['message'])

    def test_septic_endpoint_success_has_septic(self):
        # Note, this is an integration test as it utilizes a call to the
        # live mock endpoint at:
        # https://virtserver.swaggerhub.com/jmyatt/housecanary-mock/1.0.0/property-details
        response = self.send_post_request()
        self.assertEqual(response.status_code, 200)

        content_dict = loads(response.content)
        self.assertIsNone(content_dict.get('error'))
        self.assertEqual(content_dict['result'], 'septic')

    def test_septic_endpoint_success_does_not_have_septic(self):
        # Our live mock endpoint does not supply alternate output in response
        # to input parameters, so let's mock the return value from our
        # function containing the remote call
        with patch(
            'property_inspector_api.utils.get_external_property_info',
            return_value={
                'result': {
                    'property': {
                        'sewer': 'municipal'
                    }
                }
            }
        ):
            response = self.send_post_request(params=self.params_without_septic)
            self.assertEqual(response.status_code, 200)

            content_dict = loads(response.content)
            self.assertIsNone(content_dict.get('error'))
            self.assertEqual(content_dict['result'], 'not septic')
