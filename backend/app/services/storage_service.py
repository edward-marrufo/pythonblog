# /backend/app/services/storage_service.py
import datetime
import google.auth

from google.auth import credentials
from google.cloud import iam_credentials_v1, storage

class IAMSigner(credentials.Signing):
    """
    Provides the signing interface required by GCS
    library without requiring a service account private key.

    Instead of signing locally without a json key, this class
    asks Google's IAM credentials API to sign the data.
    """

    def __init__(
        self,
        credentials: credentials.Credentials,
        service_account_email: str,
    ) -> None:
        # Store the ADC credentials used to authenticate
        # requests to the IAM Credentials API.
        self._credentials = credentials

        # Store the email address of the service account that 
        # will perform the signing operation.
        self._service_account_email = service_account_email

        # Create the client used to communicate with the
        # IAM Credentials API
        self._iam_client = iam.iam_credentials_v1.IAMCredentialsClient(
            credentials=credentials
        )

    @property
    def signer_email(self) -> str:
        """
        Return the email address of the service account
        performing the signing operation.
        """

        return self._service_account_email

    def sign_bytes(self, message: bytes) -> bytes:
        """
        Ask Google IAM to sign the supplied bytes.

        The private signing key doesn't exist inside
        the application or the container.
        """

        # Construct the resource name expected
        # by the IAM Credentials API
        name = (
            f"projects/-/serviceAccounts"
            f"{self._service_account_email}"
        )

        # Ask Google IAM to cryptographically sign the data.
        response = self._iam_client.sign_blob(
            request = {
                "name": name,
                "payload": message,
            }
        )

        # Return the signature to the GCS library
        # so that it can finish constructing the signed URL.
        return response.signed_blog

class StorageService:
    """
    Provides the app interface to GCS. This class hides
    Google authentication and signing implementation
    details from the fastAPI routers and other code
    """

    def __init__(self, bucket_name: str) -> None: 
        # Obtain Application Default Credentials.

        # On the Compute VM, these creds come through
        # from the service account attached to the VM
        # through the metadata server.
        adc_credentials, project_id = google.auth.default()

        # Determine which service account the ADC credentials
        # represent.
        service_account_email = adc_credentials.service_account_email

        # Creating our custom signer. This allows the GCS library
        # to generate signed URLs without requiring a 
        # json private key file
        self._signer = IAMSigner(
            adc_credentials,
            service_account_email,
        )

        # Create the GCS client. This client uses the same ADC
        # credentials for normal GCS API operations.
        self._client = storage.Client(
            credentials = adc_credentials,
            project = project_id,
        )

        # Store the bucket name
        self._bucket_name = bucket_name

        def generate_download_url(
            self,
            object_name: str,
            expiration_minutes: int = 15,
        ) -> str:
            """
            Generate a temporary signed URL that allows the api caller
            to download a GCS object.
            """

            # Get a python representation of the requested object.
            blob = bucket.blob(object_name)

            # Generate a V4 signed URL.

            # The URL will authorize a GET request for the specified 
            # number of minutes.
            return blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(
                    minutes=expiration_minutes
                ),
                method="GET",
                credentials=self._signer,
            )