import certifi
import grpc
import os

from jarvis_sdk.cmdconfig import helper
from jarvis_sdk.indykite.config.v1beta1 import config_management_api_pb2_grpc as config_pb2_grpc


class ConfigClient(object):

    def __init__(self, local=False):
        cred = os.getenv('INDYKITE_SERVICE_ACCOUNT_CREDENTIALS')

        # Load the config from File (secondary)
        if (cred is False) or (cred is None):
            cred = os.getenv('INDYKITE_SERVICE_ACCOUNT_CREDENTIALS_FILE')
            try:
                if (cred is False) or (cred is None):
                    raise Exception("Missing INDYKITE_SERVICE_ACCOUNT_CREDENTIALS or INDYKITE_SERVICE_ACCOUNT_CREDENTIALS_FILE environment variable")
            except Exception as exception:
                print(exception)
                return None
            credentials = os.path.join(os.path.dirname(cred), os.path.basename(cred))
            credentials = helper.load_credentials(credentials)

        # Load the credential json (primary)
        else:
            credentials = helper.load_json(cred)

        service_account_token = helper.create_agent_jwt(credentials)

        call_credentials = grpc.access_token_call_credentials(service_account_token.decode("utf-8"))

        if local:
            certificate_path = os.getenv('CAPEM')
            endpoint = credentials.get("local_endpoint")
        else:
            certificate_path = certifi.where()
            endpoint = credentials.get("endpoint")

        with open(certificate_path, "rb") as cert_file:
            channel_credentials = grpc.ssl_channel_credentials(cert_file.read())

        composite_credentials = grpc.composite_channel_credentials(channel_credentials,
                                                                   call_credentials)

        self.channel = grpc.secure_channel(endpoint, composite_credentials)
        self.stub = config_pb2_grpc.ConfigManagementAPIStub(channel=self.channel)
        self.credentials = credentials

    # Imported methods
    from ._customer import get_customer_by_id, get_customer_by_name
    from ._service_account import get_service_account
    from ._app_space import get_app_space_by_id, get_app_space_by_name, create_app_space, update_app_space, list_app_spaces, delete_app_space
    from ._tenant import get_tenant_by_id, get_tenant_by_name, create_tenant, update_tenant, list_tenants, delete_tenant
    from ._application import get_application_by_id, get_application_by_name, create_application, update_application, list_applications, delete_application
    from ._application_agent import get_application_agent_by_id, get_application_agent_by_name, create_application_agent, update_application_agent, \
        list_application_agents, delete_application_agent

