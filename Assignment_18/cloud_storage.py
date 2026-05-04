"""
Cloud Storage Module
Handles uploading images and results to Azure Blob Storage.
Supports both real Azure connection and local simulator mode.
"""

import logging
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """
    Azure Blob Storage abstraction for storing fruit images and results.
    Supports real Azure connection and local simulator mode.
    """
    
    def __init__(self, connection_string='', container_name='fruit-images', 
                 simulator_mode=True):
        """
        Initialize cloud storage.
        
        Args:
            connection_string: Azure Storage connection string
            container_name: Blob container name
            simulator_mode: If True, use local file system; if False, use Azure
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.simulator_mode = simulator_mode
        self.upload_count = 0
        
        # Local simulator storage
        self.local_store = Path('./cloud_storage')
        
        if simulator_mode:
            self.local_store.mkdir(parents=True, exist_ok=True)
            logger.info("CloudStorageManager initialized in SIMULATOR mode")
        else:
            self._init_azure()
    
    def _init_azure(self):
        """Initialize Azure Blob Storage client."""
        try:
            from azure.storage.blob import BlobServiceClient
            
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            # Ensure container exists
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            
            try:
                container_client.get_container_properties()
                logger.info(f"Connected to Azure container: {self.container_name}")
            except:
                logger.info(f"Creating Azure container: {self.container_name}")
                self.blob_service_client.create_container(self.container_name)
        
        except ImportError:
            logger.error("azure-storage-blob not installed - using simulator")
            self.simulator_mode = True
        except Exception as e:
            logger.error(f"Azure connection error: {e} - using simulator")
            self.simulator_mode = True
    
    def upload_blob(self, local_file_path: str, blob_name: str) -> bool:
        """
        Upload file to blob storage.
        
        Args:
            local_file_path: Path to local file
            blob_name: Name for blob in cloud
        
        Returns:
            True if successful, False otherwise
        """
        try:
            local_path = Path(local_file_path)
            
            if not local_path.exists():
                logger.error(f"File not found: {local_file_path}")
                return False
            
            if self.simulator_mode:
                return self._upload_simulated(local_file_path, blob_name)
            else:
                return self._upload_azure(local_file_path, blob_name)
        
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False
    
    def _upload_simulated(self, local_file_path: str, blob_name: str) -> bool:
        """Simulate blob upload using local file system."""
        try:
            import shutil
            
            local_path = Path(local_file_path)
            
            # Create container directory
            container_dir = self.local_store / self.container_name
            container_dir.mkdir(parents=True, exist_ok=True)
            
            # Create blob path with directory structure
            blob_dir = container_dir / Path(blob_name).parent
            blob_dir.mkdir(parents=True, exist_ok=True)
            
            destination = container_dir / blob_name
            
            # Copy file
            shutil.copy2(local_path, destination)
            
            self.upload_count += 1
            logger.info(f"Simulated upload: {blob_name} → {destination}")
            
            # Store metadata
            self._store_metadata(blob_name, local_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Simulated upload error: {e}")
            return False
    
    def _upload_azure(self, local_file_path: str, blob_name: str) -> bool:
        """Upload blob to Azure Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            with open(local_file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            self.upload_count += 1
            logger.info(f"Azure upload: {blob_name}")
            
            # Store metadata
            self._store_metadata(blob_name, Path(local_file_path))
            
            return True
        
        except Exception as e:
            logger.error(f"Azure upload error: {e}")
            return False
    
    def _store_metadata(self, blob_name: str, local_path: Path):
        """Store blob metadata locally."""
        try:
            metadata_file = self.local_store / 'metadata.jsonl'
            
            metadata = {
                'timestamp': self._get_timestamp(),
                'blob_name': blob_name,
                'container': self.container_name,
                'local_path': str(local_path),
                'size_bytes': local_path.stat().st_size if local_path.exists() else 0
            }
            
            with open(metadata_file, 'a') as f:
                f.write(json.dumps(metadata) + '\n')
            
            logger.debug(f"Metadata stored for: {blob_name}")
        
        except Exception as e:
            logger.error(f"Metadata storage error: {e}")
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def list_blobs(self) -> list:
        """
        List all blobs in container.
        
        Returns:
            List of blob names
        """
        try:
            if self.simulator_mode:
                return self._list_simulated()
            else:
                return self._list_azure()
        
        except Exception as e:
            logger.error(f"List error: {e}")
            return []
    
    def _list_simulated(self) -> list:
        """List blobs in simulator storage."""
        try:
            container_dir = self.local_store / self.container_name
            
            if not container_dir.exists():
                return []
            
            blobs = []
            for file_path in container_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(container_dir)
                    blobs.append(str(relative_path))
            
            return sorted(blobs)
        
        except Exception as e:
            logger.error(f"Simulated list error: {e}")
            return []
    
    def _list_azure(self) -> list:
        """List blobs in Azure container."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            
            blobs = [blob.name for blob in container_client.list_blobs()]
            return sorted(blobs)
        
        except Exception as e:
            logger.error(f"Azure list error: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Get storage statistics."""
        return {
            'uploads': self.upload_count,
            'container': self.container_name,
            'simulator_mode': self.simulator_mode,
            'blobs_count': len(self.list_blobs()),
            'local_store': str(self.local_store) if self.simulator_mode else 'Azure'
        }
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cloud storage cleanup complete")
