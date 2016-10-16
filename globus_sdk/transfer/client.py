import logging
import time

from globus_sdk import exc, config
from globus_sdk.base import BaseClient, merge_params
from globus_sdk.authorizers import (
    AccessTokenAuthorizer, RefreshTokenAuthorizer)
from globus_sdk.transfer.response import (
    TransferResponse, IterableTransferResponse)
from globus_sdk.transfer.paging import PaginatedResource

logger = logging.getLogger(__name__)


class TransferClient(BaseClient):
    r"""
    Client for the
    `Globus Transfer API <https://docs.globus.org/api/transfer/>`_.

    This class provides helper methods for most common resources in the
    REST API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base rest client that can be used to access any REST resource.

    There are two types of helper methods: list methods which return an
    iterator of :class:`GlobusResponse \
    <globus_sdk.response.GlobusResponse>`
    objects, and simple methods that return a single
    :class:`TransferResponse <globus_sdk.transfer.response.TransferResponse>`
    object.

    Detailed documentation is available in the official REST API
    documentation, which is linked to from the method documentation. Methods
    that allow arbitrary keyword arguments will pass the extra arguments as
    query parameters.

    **Parameters**

        ``authorizer`` (:class:`GlobusAuthorizer\
        <globus_sdk.authorizers.base.GlobusAuthorizer>`)

          An authorizer instance used for all calls to Globus Transfer

    **Examples**

    For example, you could instantiate a new ``TransferClient`` using

    >>> from globus_sdk import TransferClient
    >>> tc = TransferClient()

    and all calls made on ``tc`` will be authenticated using the access token
    implicitly passed to the :class:`AccessTokenAuthorizer
    <globus_sdk.authorizers.AccessTokenAuthorizer>`. This is the default
    behavior -- loading the access token from the config value named
    ``transfer_token``.
    """
    # disallow basic auth
    allowed_authorizer_types = [AccessTokenAuthorizer,
                                RefreshTokenAuthorizer]
    error_class = exc.TransferAPIError
    default_response_class = TransferResponse

    def __init__(self, authorizer=None, **kwargs):
        # deprecated behavior; this is a temporary backwards compatibility hack
        access_token = config.get_transfer_token(
            kwargs.get('environment', config.get_default_environ()))
        if authorizer is None and access_token is not None:
            logger.warn(('Using deprecated config token. '
                         'Switch to explicit use of AccessTokenAuthorizer'))
            authorizer = AccessTokenAuthorizer(access_token)

        BaseClient.__init__(self, "transfer", base_path="/v0.10/",
                            authorizer=authorizer, **kwargs)

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

    def get_endpoint(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> endpoint = tc.get_endpoint(endpoint_id)
        >>> print("Endpoint name:",
        >>>       endpoint["display_name"] or endpoint["canonical_name"])

        **External Documentation**

        See
        `Get Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.get_endpoint({})".format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.get(path, params=params)

    def update_endpoint(self, endpoint_id, data, **params):
        """
        ``PUT /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> epup = dict(display_name="My New Endpoint Name",
        >>>             description="Better Description")
        >>> update_result = tc.update_endpoint(endpoint_id, epup)

        **External Documentation**

        See
        `Update Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.update_endpoint({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.put(path, data, params=params)

    def create_endpoint(self, data):
        """
        ``POST /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> ep_data = {
        >>>   "DATA_TYPE": "endpoint",
        >>>   "display_name": display_name,
        >>>   "DATA": [
        >>>     {
        >>>       "DATA_TYPE": "server",
        >>>       "hostname": "gridftp.example.edu",
        >>>     },
        >>>   ],
        >>> }
        >>> create_result = tc.create_endpoint(ep_data)
        >>> endpoint_id = create_result["id"]

        **External Documentation**

        See
        `Create endpoint \
        <https://docs.globus.org/api/transfer/endpoint/#create_endpoint>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.create_endpoint(...)")
        return self.post("endpoint", data)

    def delete_endpoint(self, endpoint_id):
        """
        ``DELETE /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> delete_result = tc.delete_endpoint(endpoint_id)

        **External Documentation**

        See
        `Delete endpoint by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.delete_endpoint({})"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.delete(path)

    def endpoint_manager_monitored_endpoints(self, **params):
        """
        ``GET endpoint_manager/monitored_endpoints``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`
        """
        self.logger.info(
            "TransferClient.endpoint_manager_monitored_endpoints({})"
            .format(params))
        path = self.qjoin_path('endpoint_manager', 'monitored_endpoints')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def endpoint_search(self, filter_fulltext=None, filter_scope=None,
                        num_results=25, **params):
        r"""
        .. parsed-literal::

            GET /endpoint_search\
            ?filter_fulltext=<filter_fulltext>&filter_scope=<filter_scope>

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Search for a given string as a fulltext search:

        >>> tc = globus_sdk.TransferClient()
        >>> for ep in tc.endpoint_search('String to search for!'):
        >>>     print(ep['display_name'])

        Search for a given string, but only on endpoints that you own:

        >>> for ep in tc.endpoint_search('foo', filter_scope='my-endpoints'):
        >>>     print('{0} has ID {1}'.format(ep['display_name'], ep['id']))

        Search results are capped at a number of elements equal to the
        ``num_results`` parameter.
        If you want more than the default, 25, elements, do like so:

        >>> for ep in tc.endpoint_search('String to search for!',
        >>>                             num_results=120):
        >>>     print(ep['display_name'])

        It is important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query.
        If you attempt to exceed this limit, you will trigger a
        :class:`PaginationOverrunError <globus_sdk.exc.PaginationOverrunError>`

        >>> for ep in tc.endpoint_search('globus', # a very common string
        >>>                             num_results=1200): # num too large!
        >>>     print(ep['display_name'])

        will trigger this error.

        **External Documentation**

        For additional information, see `Endpoint Search
        <https://docs.globus.org/api/transfer/endpoint_search>`_.
        in the REST documentation for details.
        """
        merge_params(params, filter_scope=filter_scope,
                     filter_fulltext=filter_fulltext)
        self.logger.info(
            "TransferClient.endpoint_manager_monitored_endpoints({})"
            .format(params))
        return PaginatedResource(
            self.get, "endpoint_search", {'params': params},
            num_results=num_results, max_results_per_call=100,
            max_total_results=1000)

    def endpoint_autoactivate(self, endpoint_id, **params):
        r"""
        ``POST /endpoint/<endpoint_id>/autoactivate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        The following example will try to "auto" activate the endpoint
        using a credential available from another endpoint or sign in by
        the user with the same identity provider, but only if the
        endpoint is not already activated or going to expire within an
        hour (3600 seconds). If that fails, direct the user to the
        globus website to perform activation:

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
        >>> while (r["code"] == "AutoActivateFailed"):
        >>>     print("Endpoint requires manual activation, please open "
        >>>           "the following URL in a browser to activate the "
        >>>           "endpoint:")
        >>>     print("https://www.globus.org/app/endpoints/%s/activate"
        >>>           % ep_id)
        >>>     # For python 2.X, use raw_input() instead
        >>>     input("Press ENTER after activating the endpoint:")
        >>>     r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)

        This is the recommended flow for most thick client applications,
        because many endpoints require activation via OAuth MyProxy,
        which must be done in a browser anyway. Web based clients can
        link directly to the URL.

        **External Documentation**

        See
        `Autoactivate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#autoactivate_endpoint>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.endpoint_autoactivate({})"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def endpoint_deactivate(self, endpoint_id, **params):
        """
        ``POST /endpoint/<endpoint_id>/deactivate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Deactive endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#deactivate_endpoint>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.endpoint_deactivate({})"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id, "deactivate")
        return self.post(path, params=params)

    def endpoint_activate(self, endpoint_id, requirements_data, **params):
        """
        ``POST /endpoint/<endpoint_id>/activate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        Consider using autoactivate and web activation instead, described
        in the example for
        :meth:`~globus_sdk.TransferClient.endpoint_autoactivate`.

        **External Documentation**

        See
        `Activate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#activate_endpoint>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.endpoint_activate({})"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id, "activate")
        return self.post(path, json_body=requirements_data, params=params)

    def endpoint_get_activation_requirements(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/activation_requirements``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get activation requirements \
        <https://docs.globus.org/api/transfer/endpoint_activation/#get_activation_requirements>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def my_effective_pause_rule_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/my_effective_pause_rule_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get my effective endpoint pause rules \
        <https://docs.globus.org/api/transfer/endpoint/#get_my_effective_endpoint_pause_rules>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.my_effective_pause_rule_list({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_effective_pause_rule_list')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    # Shared Endpoints

    def my_shared_endpoint_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/my_shared_endpoint_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get shared endpoint list \
        <https://docs.globus.org/api/transfer/endpoint/#get_shared_endpoint_list>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.my_shared_endpoint_list({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_shared_endpoint_list')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def create_shared_endpoint(self, data):
        """
        ``POST /shared_endpoint``

        **Parameters**

            ``data`` (*dict*)
              A python dict representation of a ``shared_endpoint`` document

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> shared_ep_data = {
        >>>   "DATA_TYPE": "shared_endpoint",
        >>>   "host_endpoint": host_endpoint_id,
        >>>   "host_path": host_path,
        >>>   "display_name": display_name,
        >>>   # optionally specify additional endpoint fields
        >>>   "description": "my test share"
        >>> }
        >>> create_result = tc.create_shared_endpoint(shared_ep_data)
        >>> endpoint_id = create_result["id"]

        **External Documentation**

        See
        `Create shared endpoint \
        <https://docs.globus.org/api/transfer/endpoint/#create_shared_endpoint>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.create_shared_endpoint(...)")
        return self.post('shared_endpoint', json_body=data)

    # Endpoint servers

    def endpoint_server_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/server_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get endpoint server list \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_list>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.endpoint_server_list({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'server_list')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def get_endpoint_server(self, endpoint_id, server_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get endpoint server list \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_list>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.get_endpoint_server({}, {}, ...)"
                         .format(endpoint_id, server_id))
        path = self.qjoin_path("endpoint", endpoint_id,
                               "server", str(server_id))
        return self.get(path, params=params)

    def add_endpoint_server(self, endpoint_id, server_data):
        """
        ``POST /endpoint/<endpoint_id>/server``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Add endpoint server \
        <https://docs.globus.org/api/transfer/endpoint/#add_endpoint_server>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.add_endpoint_server({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path("endpoint", endpoint_id, "server")
        return self.post(path, server_data)

    def update_endpoint_server(self, endpoint_id, server_id, server_data):
        """
        ``PUT /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Update endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.update_endpoint_server({}, {}, ...)"
                         .format(endpoint_id, server_id))
        path = self.qjoin_path("endpoint", endpoint_id,
                               "server", str(server_id))
        return self.put(path, server_data)

    def delete_endpoint_server(self, endpoint_id, server_id):
        """
        ``DELETE /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.delete_endpoint_server({}, {})"
                         .format(endpoint_id, server_id))
        path = self.qjoin_path("endpoint", endpoint_id,
                               "server", str(server_id))
        return self.delete(path)

    #
    # Roles
    #

    def endpoint_role_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/role_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get list of endpoint roles \
        <https://docs.globus.org/api/transfer/endpoint_roles/#get_list_of_endpoint_roles>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.endpoint_role_list({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'role_list')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def add_endpoint_role(self, endpoint_id, role_data):
        """
        ``POST /endpoint/<endpoint_id>/role``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Create endpoint role \
        <https://docs.globus.org/api/transfer/endpoint_roles/#create_endpoint_role>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.add_endpoint_role({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'role')
        return self.post(path, role_data)

    def get_endpoint_role(self, endpoint_id, role_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/role/<role_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#get_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.get_endpoint_role({}, {}, ...)"
                         .format(endpoint_id, role_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'role', role_id)
        return self.get(path, params=params)

    def delete_endpoint_role(self, endpoint_id, role_id):
        """
        ``DELETE /endpoint/<endpoint_id>/role/<role_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#delete_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.delete_endpoint_role({}, {})"
                         .format(endpoint_id, role_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'role', role_id)
        return self.delete(path)

    #
    # ACLs
    #

    def endpoint_acl_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/access_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`
        """
        self.logger.info("TransferClient.endpoint_acl_list({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'access_list')
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def get_endpoint_acl_rule(self, endpoint_id, rule_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.get_endpoint_acl_rule({}, {}, ...)"
                         .format(endpoint_id, rule_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.get(path, params=params)

    def add_endpoint_acl_rule(self, endpoint_id, rule_data):
        """
        ``POST /endpoint/<endpoint_id>/access``

        **Parameters**

            ``endpoint_id`` (*string*)
              ID of endpoint to which to add the acl

            ``rule_data`` (*dict*)
              A python dict representation of an ``access`` document

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> rule_data = {
        >>>   "DATA_TYPE": "access",
        >>>   "principal_type": "identity",
        >>>   "principal": identity_id,
        >>>   "path": "/dataset1/",
        >>>   "permissions": "rw",
        >>> }
        >>> result = tc.add_endpoint_acl_rule(endpoint_id, rule_data)
        >>> rule_id = result["id"]

        **External Documentation**

        See
        `Create access rule \
        <https://docs.globus.org/api/transfer/acl/#rest_access_create>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.add_endpoint_acl_rule({}, ...)"
                         .format(endpoint_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'access')
        return self.post(path, rule_data)

    def update_endpoint_acl_rule(self, endpoint_id, rule_id, rule_data):
        """
        ``PUT /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.update_endpoint_acl_rule({}, {}, ...)"
                         .format(endpoint_id, rule_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.put(path, rule_data)

    def delete_endpoint_acl_rule(self, endpoint_id, rule_id):
        """
        ``DELETE /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.delete_endpoint_acl_rule({}, {})"
                         .format(endpoint_id, rule_id))
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.delete(path)

    #
    # Bookmarks
    #

    def bookmark_list(self, **params):
        """
        ``GET /bookmark_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`
        """
        self.logger.info("TransferClient.bookmark_list({})".format(params))
        return self.get('bookmark_list', params=params,
                        response_class=IterableTransferResponse)

    def create_bookmark(self, bookmark_data):
        """
        ``POST /bookmark``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.create_bookmark({})"
                         .format(bookmark_data))
        return self.post('bookmark', bookmark_data)

    def get_bookmark(self, bookmark_id, **params):
        """
        ``GET /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.get_bookmark({})".format(bookmark_id))
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.get(path, params=params)

    def update_bookmark(self, bookmark_id, bookmark_data):
        """
        ``PUT /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.update_bookmark({})"
                         .format(bookmark_id))
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.put(path, bookmark_data)

    def delete_bookmark(self, bookmark_id):
        """
        ``DELETE /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.delete_bookmark({})"
                         .format(bookmark_id))
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.delete(path)

    #
    # Synchronous Filesys Operations
    #

    def operation_ls(self, endpoint_id, **params):
        """
        ``GET /operation/endpoint/<endpoint_id>/ls``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> for entry in tc.operation_ls(ep_id, path="/~/project1/"):
        >>>     print(entry["name"], entry["type"])

        **External Documentation**

        See
        `List Directory Contents \
        <https://docs.globus.org/api/transfer/file_operations/#list_directory_contents>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.operation_ls({}, {})"
                         .format(endpoint_id, params))
        path = self.qjoin_path("operation/endpoint", endpoint_id, "ls")
        return self.get(path, params=params,
                        response_class=IterableTransferResponse)

    def operation_mkdir(self, endpoint_id, path, **params):
        """
        ``POST /operation/endpoint/<endpoint_id>/mkdir``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> tc.operation_mkdir(ep_id, path="/~/newdir/")

        **External Documentation**

        See
        `Make Directory \
        <https://docs.globus.org/api/transfer/file_operations/#make_directory>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.operation_mkdir({}, {}, {})"
                         .format(endpoint_id, path, params))
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id,
                                        "mkdir")
        json_body = {
            'DATA_TYPE': 'mkdir',
            'path': path
        }
        return self.post(resource_path, json_body=json_body, params=params)

    def operation_rename(self, endpoint_id, oldpath, newpath, **params):
        """
        ``POST /operation/endpoint/<endpoint_id>/rename``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> tc.operation_rename(ep_id, oldpath="/~/file1.txt",
        >>>                     newpath="/~/project1data.txt")

        **External Documentation**

        See
        `Rename \
        <https://docs.globus.org/api/transfer/file_operations/#rename>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.operation_rename({}, {}, {}, {})"
                         .format(endpoint_id, oldpath, newpath, params))
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id,
                                        "rename")
        json_body = {
            'DATA_TYPE': 'mkdir',
            'old_path': oldpath,
            'new_path': newpath
        }
        return self.post(resource_path, json_body=json_body, params=params)

    #
    # Task Submission
    #

    def get_submission_id(self, **params):
        """
        ``GET /submission_id``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.get_submission_id({})".format(params))
        return self.get("submission_id", params=params)

    def submit_transfer(self, data):
        """
        ``POST /transfer``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> tdata = globus_sdk.TransferData(tc, source_endpoint_id,
        >>>                                 destination_endpoint_id,
        >>>                                 label="SDK example",
        >>>                                 sync_level="checksum")
        >>> tdata.add_item("/source/path/dir/", "/dest/path/dir/",
        >>>                recursive=True)
        >>> tdata.add_item("/source/path/file.txt",
        >>>                "/dest/path/file.txt")
        >>> transfer_result = tc.submit_transfer(tdata)
        >>> print("task_id =", transfer_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`TransferData <globus_sdk.TransferData>` object.

        **External Documentation**

        See
        `Submit a transfer task \
        <https://docs.globus.org/api/transfer/task_submit/#submit_a_transfer_task>`_
        in the REST documentation for more details.
        """
        self.logger.info("TransferClient.submit_transfer(...)")
        return self.post('/transfer', data)

    def submit_delete(self, data):
        """
        ``POST /delete``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient()
        >>> ddata = globus_sdk.DeleteData(tc, endpoint_id, recursive=True)
        >>> ddata.add_item("/dir/to/delete/")
        >>> ddata.add_item("/file/to/delete/file.txt")
        >>> delete_result = tc.submit_delete(ddata)
        >>> print("task_id =", delete_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`DeleteData <globus_sdk.DeleteData>` object.

        **External Documentation**

        See
        `Submit a delete task \
        <https://docs.globus.org/api/transfer/task_submit/#submit_a_delete_task>`_
        in the REST documentation for details.
        """
        self.logger.info("TransferClient.submit_delete(...)")
        return self.post('/delete', data)

    #
    # Task inspection and management
    #

    def endpoint_manager_task_list(self, num_results=10, **params):
        """
        ``GET endpoint_manager/task_list``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`
        """
        self.logger.info("TransferClient.endpoint_manager_task_list(...)")
        path = self.qjoin_path('endpoint_manager', 'task_list')
        return PaginatedResource(
            self.get, path, {'params': params},
            num_results=num_results, max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_HAS_NEXT)

    def task_list(self, num_results=10, **params):
        """
        ``GET /task_list``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`
        """
        self.logger.info("TransferClient.task_list(...)")
        return PaginatedResource(
            self.get, 'task_list', {'params': params},
            num_results=num_results, max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_TOTAL)

    def task_event_list(self, task_id, num_results=10, **params):
        """
        ``GET /task/<task_id>/event_list``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`
        """
        self.logger.info("TransferClient.task_event_list({}, ...)"
                         .format(task_id))
        path = self.qjoin_path('task', task_id, 'event_list')
        return PaginatedResource(
            self.get, path, {'params': params},
            num_results=num_results, max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_TOTAL)

    def get_task(self, task_id, **params):
        """
        ``GET /task/<task_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.get_task({}, ...)".format(task_id))
        resource_path = self.qjoin_path("task", task_id)
        return self.get(resource_path, params=params)

    def update_task(self, task_id, data, **params):
        """
        ``PUT /task/<task_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.update_task({}, ...)".format(task_id))
        resource_path = self.qjoin_path("task", task_id)
        return self.put(resource_path, data, params=params)

    def cancel_task(self, task_id):
        """
        ``POST /task/<task_id>/cancel``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.cancel_task({})".format(task_id))
        resource_path = self.qjoin_path("task", task_id, "cancel")
        return self.post(resource_path)

    def task_wait(self, task_id, timeout=10, polling_interval=10):
        r"""
        Wait until a Task is complete or fails, with a time limit. If the task
        is "ACTIVE" after time runs out, returns ``False``. Otherwise returns
        ``True``.

        **Parameters**

            ``task_id`` (*string*)
              ID of the Task to wait on for completion

            ``timeout`` (*int*)
              Number of seconds to wait in total. Minimum 1

            ``polling_interval`` (*int*)
              Number of seconds between queries to Globus about the Task
              status. Minimum 1

        **Examples**

        If you want to wait for a task to terminate, but want to warn every
        minute that it doesn't terminate, you could:

        >>> tc = TransferClient()
        >>> while not tc.task_wait(task_id, timeout=60):
        >>>     print("Another minute went by without {0} terminating"
        >>>           .format(task_id))

        Or perhaps you want to check on a task every minute for 10 minutes, and
        give up if it doesn't complete in that time:

        >>> tc = TransferClient()
        >>> done = tc.task_wait(task_id, timeout=600, polling_interval=60):
        >>> if not done:
        >>>     print("{0} didn't successfully terminate!"
        >>>           .format(task_id))
        >>> else:
        >>>     print("{0} completed".format(task_id))

        You could print dots while you wait for a task by only waiting one
        second at a time:

        >>> tc = TransferClient()
        >>> while not tc.task_wait(task_id, timeout=1, polling_interval=1):
        >>>     print(".", end="")
        >>> print("\n{0} completed!".format(task_id))
        """
        self.logger.info("TransferClient.task_wait({}, {}, {})"
                         .format(task_id, timeout, polling_interval))

        # check valid args
        if timeout < 1:
            self.logger.error(
                "task_wait() timeout={} is less than minimum of 1s"
                .format(timeout))
            raise ValueError(
                "TransferClient.task_wait timeout has a minimum of 1")
        if polling_interval < 1:
            self.logger.error(
                "task_wait() polling_interval={} is less than minimum of 1s"
                .format(polling_interval))
            raise ValueError(
                "TransferClient.task_wait polling_interval has a minimum of 1")

        # ensure that we always wait at least one interval, even if the timeout
        # is shorter than the polling interval, by reducing the interval to the
        # timeout if it is larger
        polling_interval = min(timeout, polling_interval)

        # helper for readability
        def timed_out(waited_time):
            return waited_time > timeout

        waited_time = 0
        # doing this as a while-True loop actually makes it simpler than doing
        # while not timed_out(waited_time) because of the end condition
        while True:
            # get task, check if status != ACTIVE
            task = self.get_task(task_id)
            status = task['status']
            if status != 'ACTIVE':
                self.logger.debug(
                    "task_wait(task_id={}) terminated with status={}"
                    .format(task_id, status))
                return True

            # make sure to check if we timed out before sleeping again, so we
            # don't sleep an extra polling_interval
            waited_time += polling_interval
            if timed_out(waited_time):
                self.logger.debug(
                    "task_wait(task_id={}) timed out".format(task_id))
                return False

            self.logger.debug(
                "task_wait(task_id={}) waiting {}s"
                .format(task_id, polling_interval))
            time.sleep(polling_interval)
        # unreachable -- end of task_wait

    def task_pause_info(self, task_id, **params):
        """
        ``POST /task/<task_id>/pause_info``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`
        """
        self.logger.info("TransferClient.task_pause_info({}, ...)"
                         .format(task_id))
        resource_path = self.qjoin_path("task", task_id, "pause_info")
        return self.get(resource_path, params=params)
