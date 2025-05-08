"""
Tests for S3-compatible object storage interface.
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from botocore.exceptions import ClientError

from top_songs.storage.object_store.s3 import ObjectStoreInterface
from top_songs.core.config import ObjectStoreSettings


@pytest.fixture
def mock_client():
    """Mock boto3 S3 client."""
    client = MagicMock()
    
    # Setup default return values
    client.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'region=US/date=2023-01-01/hour=01/data.parquet', 'Size': 1024},
            {'Key': 'region=US/date=2023-01-01/hour=02/data.parquet', 'Size': 2048}
        ]
    }
    client.head_object.return_value = {'ContentLength': 1024, 'ContentType': 'application/octet-stream'}
    client.generate_presigned_url.return_value = "https://example.com/presigned-url"
    
    # Setup methods that should return True/False
    client.head_bucket.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    client.upload_file.return_value = None
    client.upload_fileobj.return_value = None
    client.put_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    client.download_file.return_value = None
    client.download_fileobj.return_value = None
    client.delete_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 204}}
    
    return client


@pytest.fixture
def mock_resource():
    """Mock boto3 S3 resource."""
    return MagicMock()


@pytest.fixture
def object_store_interface():
    """Create an ObjectStoreInterface instance with test parameters."""
    return ObjectStoreInterface(
        endpoint_url="http://localhost:9000",
        access_key="test-access-key",
        secret_key="test-secret-key",
        secure=False,
        region="us-east-1",
        bucket_name="test-bucket"
    )


def test_init_with_direct_params():
    """Test initialization with direct parameters."""
    interface = ObjectStoreInterface(
        endpoint_url="minio:9000",
        access_key="test-key",
        secret_key="test-secret",
        secure=True,
        region="eu-west-1",
        bucket_name="custom-bucket"
    )
    
    assert interface.endpoint_url == "https://minio:9000"  # Protocol added
    assert interface.access_key == "test-key"
    assert interface.secret_key == "test-secret"
    assert interface.secure is True
    assert interface.region == "eu-west-1"
    assert interface.bucket_name == "custom-bucket"


def test_init_with_settings():
    """Test initialization using settings."""
    # Mock the settings
    mock_settings = MagicMock()
    mock_settings.object_store = ObjectStoreSettings(
        endpoint="minio:9000",
        access_key="settings-key",
        secret_key="settings-secret"
    )
    mock_settings.object_store.region = "us-west-2"
    mock_settings.object_store.bucket_name = "settings-bucket"
    
    with patch('top_songs.storage.object_store.s3.settings', mock_settings):
        # Create with no explicit params - should use settings
        interface = ObjectStoreInterface()
        
        assert interface.endpoint_url == "http://minio:9000"  # Protocol added
        assert interface.access_key == "settings-key"
        assert interface.secret_key == "settings-secret"
        assert interface.region == "us-west-2"
        assert interface.bucket_name == "settings-bucket"


def test_init_with_missing_settings():
    """Test initialization with missing settings."""
    with patch('top_songs.storage.object_store.s3.settings', None):
        # Should raise ValueError when required parameters are missing
        with pytest.raises(ValueError, match="Missing required object store parameters"):
            ObjectStoreInterface()
        
        # Should work with all required parameters
        interface = ObjectStoreInterface(
            endpoint_url="localhost:9000",
            access_key="test-key",
            secret_key="test-secret",
            bucket_name="test-bucket"
        )
        assert interface.endpoint_url == "http://localhost:9000"
        assert interface.access_key == "test-key"
        assert interface.secret_key == "test-secret"
        assert interface.bucket_name == "test-bucket"


def test_client_property(object_store_interface):
    """Test client property creates boto3 client with correct parameters."""
    with patch('boto3.client') as mock_client_constructor:
        mock_client_instance = MagicMock()
        mock_client_constructor.return_value = mock_client_instance
        
        # Access the client property
        _ = object_store_interface.client
        
        # Verify client was created with correct parameters
        mock_client_constructor.assert_called_once_with(
            's3',
            endpoint_url=object_store_interface.endpoint_url,
            aws_access_key_id=object_store_interface.access_key,
            aws_secret_access_key=object_store_interface.secret_key,
            region_name=object_store_interface.region,
            use_ssl=object_store_interface.secure
        )
        
        # Verify client is cached
        assert object_store_interface._client == mock_client_instance
        
        # Access again - should use cached client
        _ = object_store_interface.client
        assert mock_client_constructor.call_count == 1  # Still just one call


def test_resource_property(object_store_interface):
    """Test resource property creates boto3 resource with correct parameters."""
    with patch('boto3.resource') as mock_resource_constructor:
        mock_resource_instance = MagicMock()
        mock_resource_constructor.return_value = mock_resource_instance
        
        # Access the resource property
        _ = object_store_interface.resource
        
        # Verify resource was created with correct parameters
        mock_resource_constructor.assert_called_once_with(
            's3',
            endpoint_url=object_store_interface.endpoint_url,
            aws_access_key_id=object_store_interface.access_key,
            aws_secret_access_key=object_store_interface.secret_key,
            region_name=object_store_interface.region,
            use_ssl=object_store_interface.secure
        )
        
        # Verify resource is cached
        assert object_store_interface._resource == mock_resource_instance


def test_bucket_exists_success(object_store_interface, mock_client):
    """Test bucket_exists when bucket exists."""
    object_store_interface._client = mock_client
    
    # Test with default bucket
    result = object_store_interface.bucket_exists()
    
    # Verify head_bucket was called with correct bucket
    mock_client.head_bucket.assert_called_once_with(Bucket="test-bucket")
    assert result is True
    
    # Reset mock and test with specific bucket
    mock_client.reset_mock()
    result = object_store_interface.bucket_exists("other-bucket")
    
    # Verify head_bucket was called with specified bucket
    mock_client.head_bucket.assert_called_once_with(Bucket="other-bucket")
    assert result is True


def test_bucket_exists_failure(object_store_interface, mock_client):
    """Test bucket_exists when bucket doesn't exist."""
    object_store_interface._client = mock_client
    
    # Make head_bucket raise ClientError
    mock_client.head_bucket.side_effect = ClientError(
        {'Error': {'Code': '404', 'Message': 'Not Found'}},
        'HeadBucket'
    )
    
    result = object_store_interface.bucket_exists()
    
    # Verify head_bucket was called
    mock_client.head_bucket.assert_called_once()
    assert result is False


def test_create_bucket_success(object_store_interface, mock_client):
    """Test create_bucket when bucket doesn't exist."""
    object_store_interface._client = mock_client
    
    # Make bucket_exists return False to simulate bucket not existing
    with patch.object(object_store_interface, 'bucket_exists', return_value=False):
        result = object_store_interface.create_bucket()
    
    # Verify create_bucket was called with correct bucket
    mock_client.create_bucket.assert_called_once()
    assert result is True
    
    # Test with non-default region
    mock_client.reset_mock()
    object_store_interface.region = "eu-west-1"
    
    with patch.object(object_store_interface, 'bucket_exists', return_value=False):
        result = object_store_interface.create_bucket()
    
    # Verify LocationConstraint was specified for non-us-east-1 region
    mock_client.create_bucket.assert_called_once()
    call_kwargs = mock_client.create_bucket.call_args[1]
    assert 'CreateBucketConfiguration' in call_kwargs
    assert call_kwargs['CreateBucketConfiguration'] == {'LocationConstraint': 'eu-west-1'}


def test_create_bucket_already_exists(object_store_interface, mock_client):
    """Test create_bucket when bucket already exists."""
    object_store_interface._client = mock_client
    
    # Make bucket_exists return True to simulate bucket existing
    with patch.object(object_store_interface, 'bucket_exists', return_value=True):
        result = object_store_interface.create_bucket()
    
    # Verify create_bucket was not called
    mock_client.create_bucket.assert_not_called()
    assert result is False


def test_upload_file(object_store_interface, mock_client):
    """Test upload_file method."""
    object_store_interface._client = mock_client
    
    # Test with explicit object key
    result = object_store_interface.upload_file("/path/to/local/file.txt", "path/in/bucket.txt")
    
    # Verify upload_file was called with correct parameters
    mock_client.upload_file.assert_called_once_with(
        "/path/to/local/file.txt", "test-bucket", "path/in/bucket.txt"
    )
    assert result is True
    
    # Test with default object key (basename of file_path)
    mock_client.reset_mock()
    result = object_store_interface.upload_file("/path/to/local/file.txt")
    
    mock_client.upload_file.assert_called_once_with(
        "/path/to/local/file.txt", "test-bucket", "file.txt"
    )
    assert result is True


def test_upload_file_failure(object_store_interface, mock_client):
    """Test upload_file when it fails."""
    object_store_interface._client = mock_client
    
    # Make upload_file raise ClientError
    mock_client.upload_file.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'UploadFile'
    )
    
    result = object_store_interface.upload_file("/path/to/local/file.txt")
    
    # Verify method was called
    mock_client.upload_file.assert_called_once()
    assert result is False


def test_upload_fileobj(object_store_interface, mock_client):
    """Test upload_fileobj method."""
    object_store_interface._client = mock_client
    
    # Create a BytesIO object to use as file_obj
    file_obj = BytesIO(b"test data")
    
    result = object_store_interface.upload_fileobj(file_obj, "path/in/bucket.txt")
    
    # Verify upload_fileobj was called with correct parameters
    mock_client.upload_fileobj.assert_called_once_with(
        file_obj, "test-bucket", "path/in/bucket.txt"
    )
    assert result is True


def test_upload_fileobj_failure(object_store_interface, mock_client):
    """Test upload_fileobj when it fails."""
    object_store_interface._client = mock_client
    
    # Make upload_fileobj raise ClientError
    mock_client.upload_fileobj.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'UploadFileObj'
    )
    
    file_obj = BytesIO(b"test data")
    result = object_store_interface.upload_fileobj(file_obj, "path/in/bucket.txt")
    
    # Verify method was called
    mock_client.upload_fileobj.assert_called_once()
    assert result is False


def test_upload_data_string(object_store_interface, mock_client):
    """Test upload_data with string data."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.upload_data("test string data", "path/in/bucket.txt")
    
    # Verify put_object was called with bytes data (string converted to UTF-8)
    mock_client.put_object.assert_called_once()
    call_args = mock_client.put_object.call_args[1]
    assert call_args['Bucket'] == "test-bucket"
    assert call_args['Key'] == "path/in/bucket.txt"
    assert isinstance(call_args['Body'], bytes)
    assert call_args['Body'] == b"test string data"
    assert result is True


def test_upload_data_bytes(object_store_interface, mock_client):
    """Test upload_data with bytes data."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.upload_data(b"test bytes data", "path/in/bucket.txt")
    
    # Verify put_object was called with bytes data
    mock_client.put_object.assert_called_once()
    call_args = mock_client.put_object.call_args[1]
    assert call_args['Body'] == b"test bytes data"
    assert result is True


def test_upload_data_failure(object_store_interface, mock_client):
    """Test upload_data when it fails."""
    object_store_interface._client = mock_client
    
    # Make put_object raise ClientError
    mock_client.put_object.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'PutObject'
    )
    
    result = object_store_interface.upload_data("test data", "path/in/bucket.txt")
    
    # Verify method was called
    mock_client.put_object.assert_called_once()
    assert result is False


def test_download_file(object_store_interface, mock_client):
    """Test download_file method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.download_file("path/in/bucket.txt", "/path/to/local/file.txt")
    
    # Verify download_file was called with correct parameters
    mock_client.download_file.assert_called_once_with(
        "test-bucket", "path/in/bucket.txt", "/path/to/local/file.txt"
    )
    assert result is True


def test_download_file_failure(object_store_interface, mock_client):
    """Test download_file when it fails."""
    object_store_interface._client = mock_client
    
    # Make download_file raise ClientError
    mock_client.download_file.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'DownloadFile'
    )
    
    result = object_store_interface.download_file("path/in/bucket.txt", "/path/to/local/file.txt")
    
    # Verify method was called
    mock_client.download_file.assert_called_once()
    assert result is False


def test_download_fileobj(object_store_interface, mock_client):
    """Test download_fileobj method."""
    object_store_interface._client = mock_client
    
    # Set up mock to simulate download into BytesIO
    def side_effect(bucket, key, file_obj):
        file_obj.write(b"test downloaded data")
    
    mock_client.download_fileobj.side_effect = side_effect
    
    result = object_store_interface.download_fileobj("path/in/bucket.txt")
    
    # Verify download_fileobj was called with correct parameters
    mock_client.download_fileobj.assert_called_once()
    call_args = mock_client.download_fileobj.call_args[0]
    assert call_args[0] == "test-bucket"
    assert call_args[1] == "path/in/bucket.txt"
    assert isinstance(call_args[2], BytesIO)
    
    # Verify result is BytesIO with expected content
    assert isinstance(result, BytesIO)
    assert result.getvalue() == b"test downloaded data"


def test_download_fileobj_failure(object_store_interface, mock_client):
    """Test download_fileobj when it fails."""
    object_store_interface._client = mock_client
    
    # Make download_fileobj raise ClientError
    mock_client.download_fileobj.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'DownloadFileObj'
    )
    
    result = object_store_interface.download_fileobj("path/in/bucket.txt")
    
    # Verify method was called
    mock_client.download_fileobj.assert_called_once()
    assert result is None


def test_delete_object(object_store_interface, mock_client):
    """Test delete_object method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.delete_object("path/in/bucket.txt")
    
    # Verify delete_object was called with correct parameters
    mock_client.delete_object.assert_called_once_with(
        Bucket="test-bucket", Key="path/in/bucket.txt"
    )
    assert result is True


def test_delete_object_failure(object_store_interface, mock_client):
    """Test delete_object when it fails."""
    object_store_interface._client = mock_client
    
    # Make delete_object raise ClientError
    mock_client.delete_object.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'DeleteObject'
    )
    
    result = object_store_interface.delete_object("path/in/bucket.txt")
    
    # Verify method was called
    mock_client.delete_object.assert_called_once()
    assert result is False


def test_list_objects(object_store_interface, mock_client):
    """Test list_objects method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.list_objects("region=US/date=2023-01-01")
    
    # Verify list_objects_v2 was called with correct parameters
    mock_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket", Prefix="region=US/date=2023-01-01"
    )
    
    # Verify result contains the expected items from the mock response
    assert len(result) == 2
    assert result[0]['Key'] == "region=US/date=2023-01-01/hour=01/data.parquet"
    assert result[1]['Key'] == "region=US/date=2023-01-01/hour=02/data.parquet"


def test_list_objects_empty(object_store_interface, mock_client):
    """Test list_objects when no objects match the prefix."""
    object_store_interface._client = mock_client
    
    # Set up mock to return empty response
    mock_client.list_objects_v2.return_value = {}
    
    result = object_store_interface.list_objects("region=US/date=2023-01-01")
    
    # Verify method was called
    mock_client.list_objects_v2.assert_called_once()
    assert result == []


def test_list_objects_failure(object_store_interface, mock_client):
    """Test list_objects when it fails."""
    object_store_interface._client = mock_client
    
    # Make list_objects_v2 raise ClientError
    mock_client.list_objects_v2.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'ListObjectsV2'
    )
    
    result = object_store_interface.list_objects("region=US/date=2023-01-01")
    
    # Verify method was called
    mock_client.list_objects_v2.assert_called_once()
    assert result == []


def test_object_exists(object_store_interface, mock_client):
    """Test object_exists method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.object_exists("path/in/bucket.txt")
    
    # Verify head_object was called with correct parameters
    mock_client.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="path/in/bucket.txt"
    )
    assert result is True


def test_object_exists_failure(object_store_interface, mock_client):
    """Test object_exists when object doesn't exist."""
    object_store_interface._client = mock_client
    
    # Make head_object raise ClientError
    mock_client.head_object.side_effect = ClientError(
        {'Error': {'Code': '404', 'Message': 'Not Found'}},
        'HeadObject'
    )
    
    result = object_store_interface.object_exists("path/in/bucket.txt")
    
    # Verify method was called
    mock_client.head_object.assert_called_once()
    assert result is False


def test_get_object_metadata(object_store_interface, mock_client):
    """Test get_object_metadata method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.get_object_metadata("path/in/bucket.txt")
    
    # Verify head_object was called with correct parameters
    mock_client.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="path/in/bucket.txt"
    )
    
    # Verify result contains the metadata
    assert result['ContentLength'] == 1024
    assert result['ContentType'] == 'application/octet-stream'


def test_get_object_metadata_failure(object_store_interface, mock_client):
    """Test get_object_metadata when object doesn't exist."""
    object_store_interface._client = mock_client
    
    # Make head_object raise ClientError
    mock_client.head_object.side_effect = ClientError(
        {'Error': {'Code': '404', 'Message': 'Not Found'}},
        'HeadObject'
    )
    
    result = object_store_interface.get_object_metadata("path/in/bucket.txt")
    
    # Verify method was called
    mock_client.head_object.assert_called_once()
    assert result is None


def test_generate_presigned_url(object_store_interface, mock_client):
    """Test generate_presigned_url method."""
    object_store_interface._client = mock_client
    
    result = object_store_interface.generate_presigned_url("path/in/bucket.txt", expiration=3600)
    
    # Verify generate_presigned_url was called with correct parameters
    mock_client.generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={'Bucket': 'test-bucket', 'Key': 'path/in/bucket.txt'},
        ExpiresIn=3600
    )
    
    # Verify result is the URL from the mock
    assert result == "https://example.com/presigned-url"


def test_generate_presigned_url_failure(object_store_interface, mock_client):
    """Test generate_presigned_url when it fails."""
    object_store_interface._client = mock_client
    
    # Make generate_presigned_url raise ClientError
    mock_client.generate_presigned_url.side_effect = ClientError(
        {'Error': {'Code': '500', 'Message': 'Error'}},
        'GeneratePresignedUrl'
    )
    
    result = object_store_interface.generate_presigned_url("path/in/bucket.txt")
    
    # Verify method was called
    mock_client.generate_presigned_url.assert_called_once()
    assert result is None


def test_get_song_play_data(object_store_interface, mock_client):
    """Test get_song_play_data method."""
    object_store_interface._client = mock_client
    
    # Set up mock to return parquet files for a specific region/date
    mock_client.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'region=US/date=2023-01-01/hour=01/data.parquet'},
            {'Key': 'region=US/date=2023-01-01/hour=01/metadata.json'},  # Not a parquet file
            {'Key': 'region=US/date=2023-01-01/hour=02/data.parquet'}
        ]
    }
    
    # Test with both region and date
    result = object_store_interface.get_song_play_data(region="US", date="2023-01-01")
    
    # Verify list_objects_v2 was called with correct prefix
    mock_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket", Prefix="region=US/date=2023-01-01"
    )
    
    # Verify result contains only parquet files
    assert len(result) == 2
    assert result[0]['file'] == 'region=US/date=2023-01-01/hour=01/data.parquet'
    assert result[1]['file'] == 'region=US/date=2023-01-01/hour=02/data.parquet'
    
    # Test with region, date, and hour
    mock_client.reset_mock()
    mock_client.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'region=US/date=2023-01-01/hour=03/data.parquet'}
        ]
    }
    
    result = object_store_interface.get_song_play_data(region="US", date="2023-01-01", hour=3)
    
    # Verify list_objects_v2 was called with correct prefix including hour
    mock_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket", Prefix="region=US/date=2023-01-01/hour=03"
    )
    
    # Verify result contains the expected file
    assert len(result) == 1
    assert result[0]['file'] == 'region=US/date=2023-01-01/hour=03/data.parquet' 