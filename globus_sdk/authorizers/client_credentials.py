import logging

from globus_sdk.authorizers.renewing import RenewingAuthorizer
from globus_sdk.exc import GlobusError

logger = logging.getLogger(__name__)


class ClientCredentialsAuthorizer(RenewingAuthorizer):
    """
    Implementation of a RenewingAuthorizer that renews confidential app client
    Access Tokens using a ConfidentialAppAuthClient and a set of scopes to
    fetch a new Access Token when the old one expires.

    Example usage looks something like this:

    >>> import globus_sdk
    >>> confidential_client = globus_sdk.ConfidentiallAppAuthClient(
        client_id=..., client_secret=...)
    >>> cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
    >>>     confidential_client)
    >>> # create a new client
    >>> transfer_client = globus_sdk.TransferClient(authorizer=cc_authorizer)

    any client that inherits from :class:`BaseClient <globus_sdk.BaseClient>`
    should be able to use a ClientCredentialsAuthorizer to act as
    the client itself.

    **Parameters**

        ``confidential_client``(:class:`ConfidentialAppAuthClient
            <globus_sdk.ConfidentialAppAuthClient>`)
          ``ConfidentialAppAuthClient`` with a valid id and client secret

        ``scopes`` (*string*)
          A string of space-separated scope names being requested for the
          access tokens that will be used for the Authorization header.
          These scopes must all be for the same resource server, or else
          the token response will have multiple access tokens.

        ``access_token`` (*string*)
          Initial Access Token to use, only used if ``expires_at`` is also set.
          Must be requested with the same set of scopes passed to this
          authorizer.

        ``expires_at`` (*int*)
          Expiration time for the starting ``access_token`` expressed as a
          POSIX timestamp (i.e. seconds since the epoch)

        ``on_refresh`` (*callable*)
          Will be called as fn(TokenResponse) any time this authorizer
          fetches a new access_token
    """
    def __init__(self, confidential_client, scopes,
                 access_token=None, expires_at=None, on_refresh=None):
        logger.info((
            "Setting up ClientCredentialsAuthorizer with confidential_client ="
            " instance:{} and scopes = "
            "{}".format(id(confidential_client), scopes)))

        # values for _get_token_response
        self.confidential_client = confidential_client
        self.scopes = scopes

        super(ClientCredentialsAuthorizer, self).__init__(
            access_token, expires_at, on_refresh)

    def _get_token_response(self):
        """
        Return the token response from a client credentials grant.
        Make sure there is only one Access Token in the token response.
        """
        res = self.confidential_client.oauth2_client_credentials_tokens(
            requested_scopes=self.scopes)
        if res.other_tokens:
            raise GlobusError(("ClientCredentialsAuthorizer created with "
                               "scopes {} got back multiple Access Tokens. "
                               "Make sure the set of scopes are only for "
                               "one resource server.".format(self.scopes)))

        return res
