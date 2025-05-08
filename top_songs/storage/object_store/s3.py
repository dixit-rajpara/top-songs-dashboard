"""
S3-compatible object storage interface for the Top Songs application.
"""
from typing import Any, Dict, List, Optional, Union, BinaryIO
import os
import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError
from io import BytesIO
from top_songs.core.config import settings


class ObjectStoreInterface:
    """Interface for S3-compatible object storage operations.
    
    This class provides a high-level interface for interacting with
    S3-compatible object storage services like MinIO or AWS S3.
    It abstracts away the boto3 details and provides methods for
    common object storage operations.
    """
    
    def __init__(self, endpoint_url: Optional[str] = None,
                 access_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 secure: Optional[bool] = None,
                 region: Optional[str] = None,
                 bucket_name: Optional[str] = None):
        """
        Initialize the object store interface with connection parameters.
        
        Args:
            endpoint_url: Endpoint URL for the service (e.g., 'localhost:9000')
            access_key: Access key (username) for authentication
            secret_key: Secret key (password) for authentication
            secure: Whether to use HTTPS (True) or HTTP (False)
            region: AWS region or equivalent
            bucket_name: Default bucket to use for operations
        """
        if settings is None or settings.object_store is None:
            if not all([endpoint_url, access_key, secret_key, bucket_name]):
                raise ValueError("Missing required object store parameters")
            self.endpoint_url = endpoint_url
            self.access_key = access_key
            self.secret_key = secret_key
            self.secure = secure if secure is not None else False
            self.region = region or "us-east-1"
            self.bucket_name = bucket_name
        else:
            self.endpoint_url = endpoint_url or settings.object_store.endpoint
            self.access_key = access_key or settings.object_store.access_key
            self.secret_key = secret_key or settings.object_store.secret_key
            self.secure = secure if secure is not None else settings.object_store.secure
            self.region = region or settings.object_store.region
            self.bucket_name = bucket_name or settings.object_store.bucket_name
        
        # Construct proper endpoint URL with protocol
        protocol = "https" if self.secure else "http"
        if not self.endpoint_url.startswith(("http://", "https://")):
            self.endpoint_url = f"{protocol}://{self.endpoint_url}"
        
        self._client = None
        self._resource = None
    
    @property
    def client(self):
        """Get the boto3 S3 client, creating it if necessary."""
        if self._client is None:
            self._client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                use_ssl=self.secure
            )
        return self._client
    
    @property
    def resource(self):
        """Get the boto3 S3 resource, creating it if necessary."""
        if self._resource is None:
            self._resource = boto3.resource(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                use_ssl=self.secure
            )
        return self._resource
    
    def bucket_exists(self, bucket_name: Optional[str] = None) -> bool:
        """
        Check if a bucket exists.
        
        Args:
            bucket_name: Name of the bucket to check. If None, uses default bucket.
            
        Returns:
            True if the bucket exists, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            return False
    
    def create_bucket(self, bucket_name: Optional[str] = None) -> bool:
        """
        Create a new bucket.
        
        Args:
            bucket_name: Name of the bucket to create. If None, uses default bucket.
            
        Returns:
            True if bucket was created, False if it already exists.
        """
        bucket = bucket_name or self.bucket_name
        if self.bucket_exists(bucket):
            return False
        
        try:
            # For regions other than us-east-1, we need to specify the location constraint
            if self.region != "us-east-1":
                self.client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            else:
                self.client.create_bucket(Bucket=bucket)
            return True
        except ClientError:
            return False
    
    def upload_file(self, file_path: str, object_key: Optional[str] = None, 
                    bucket_name: Optional[str] = None) -> bool:
        """
        Upload a file to the object store.
        
        Args:
            file_path: Path to the local file
            object_key: Key (path) to store the object under. If None, uses basename of file_path.
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the upload was successful, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        key = object_key or os.path.basename(file_path)
        
        try:
            self.client.upload_file(file_path, bucket, key)
            return True
        except ClientError:
            return False
    
    def upload_fileobj(self, file_obj: BinaryIO, object_key: str, 
                       bucket_name: Optional[str] = None) -> bool:
        """
        Upload a file-like object to the object store.
        
        Args:
            file_obj: File-like object to upload
            object_key: Key (path) to store the object under
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the upload was successful, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.upload_fileobj(file_obj, bucket, object_key)
            return True
        except ClientError:
            return False
    
    def upload_data(self, data: Union[str, bytes], object_key: str, 
                    bucket_name: Optional[str] = None) -> bool:
        """
        Upload string or bytes data directly to the object store.
        
        Args:
            data: String or bytes data to upload
            object_key: Key (path) to store the object under
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the upload was successful, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            self.client.put_object(Body=data, Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False
    
    def download_file(self, object_key: str, file_path: str, 
                      bucket_name: Optional[str] = None) -> bool:
        """
        Download an object to a local file.
        
        Args:
            object_key: Key (path) of the object to download
            file_path: Path to save the file to
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the download was successful, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.download_file(bucket, object_key, file_path)
            return True
        except ClientError:
            return False
    
    def download_fileobj(self, object_key: str, 
                         bucket_name: Optional[str] = None) -> Optional[BytesIO]:
        """
        Download an object as a file-like object.
        
        Args:
            object_key: Key (path) of the object to download
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            BytesIO object containing the data, or None if download failed.
        """
        bucket = bucket_name or self.bucket_name
        file_obj = BytesIO()
        
        try:
            self.client.download_fileobj(bucket, object_key, file_obj)
            file_obj.seek(0)  # Reset position to beginning of file
            return file_obj
        except ClientError:
            return None
    
    def delete_object(self, object_key: str, bucket_name: Optional[str] = None) -> bool:
        """
        Delete an object from the object store.
        
        Args:
            object_key: Key (path) of the object to delete
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the deletion was successful, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.delete_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False
    
    def list_objects(self, prefix: str = "", 
                     bucket_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List objects in a bucket with the given prefix.
        
        Args:
            prefix: Prefix to filter objects by
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            List of object metadata dictionaries
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if 'Contents' in response:
                return response['Contents']
            return []
        except ClientError:
            return []
    
    def object_exists(self, object_key: str, bucket_name: Optional[str] = None) -> bool:
        """
        Check if an object exists in the bucket.
        
        Args:
            object_key: Key (path) of the object to check
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            True if the object exists, False otherwise.
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.head_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False
    
    def get_object_metadata(self, object_key: str, 
                           bucket_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an object.
        
        Args:
            object_key: Key (path) of the object
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            Dictionary of metadata or None if the object doesn't exist
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            response = self.client.head_object(Bucket=bucket, Key=object_key)
            return response
        except ClientError:
            return None
    
    def generate_presigned_url(self, object_key: str, expiration: int = 3600, 
                               bucket_name: Optional[str] = None) -> Optional[str]:
        """
        Generate a presigned URL for an object.
        
        Args:
            object_key: Key (path) of the object
            expiration: Time in seconds for the URL to remain valid
            bucket_name: Name of the bucket to use. If None, uses default bucket.
            
        Returns:
            Presigned URL string or None if generation failed
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError:
            return None
    
    # Higher-level methods specific to the Top Songs application
    
    def get_song_play_data(self, region: str, date: str, hour: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get song play data for a specific region and time period.
        
        Args:
            region: Geographic region code
            date: ISO date string (YYYY-MM-DD)
            hour: Optional hour (0-23) to filter by
            
        Returns:
            List of song play records
        """
        prefix = f"region={region}/date={date}"
        if hour is not None:
            prefix = f"{prefix}/hour={hour:02d}"
        
        # List all relevant Parquet files
        parquet_files = [obj['Key'] for obj in self.list_objects(prefix) 
                         if obj['Key'].endswith('.parquet')]
        
        # This could be enhanced to use pandas or pyarrow to read Parquet files
        # For now, we just return the list of files as metadata
        return [{'file': file} for file in parquet_files]


# Create a singleton instance for convenient import
object_store = None
try:
    if settings and settings.object_store:
        object_store = ObjectStoreInterface()
except (ImportError, ValidationError):
    # Will be initialized later when settings are available
    pass 