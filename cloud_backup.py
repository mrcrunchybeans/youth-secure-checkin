"""Cloud backup functionality for Google Drive, OneDrive, and Dropbox"""

import os
import io
import json
from datetime import datetime
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import dropbox
    from dropbox.exceptions import ApiError
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False


class GoogleDriveBackup:
    """Handle backups to Google Drive"""
    
    def __init__(self, credentials_json_path=None):
        """Initialize Google Drive client
        
        Args:
            credentials_json_path: Path to service account JSON file
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries not installed")
        
        self.service = None
        self.folder_id = None
        
        if credentials_json_path and os.path.exists(credentials_json_path):
            try:
                credentials = ServiceAccountCredentials.from_service_account_file(
                    credentials_json_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=credentials)
            except Exception as e:
                raise Exception(f"Failed to authenticate with Google Drive: {str(e)}")
    
    def upload_backup(self, backup_data, filename):
        """Upload backup file to Google Drive
        
        Args:
            backup_data: File data as bytes
            filename: Name of the file to upload
            
        Returns:
            Tuple of (success, message, file_id)
        """
        if not self.service:
            return False, "Google Drive not configured", None
        
        try:
            # Create a BytesIO object from the backup data
            file_stream = io.BytesIO(backup_data)
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Upload file
            media = MediaIoBaseUpload(file_stream, mimetype='application/json', resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return True, f"Backup uploaded to Google Drive: {filename}", file.get('id')
        
        except Exception as e:
            return False, f"Google Drive upload failed: {str(e)}", None
    
    def list_backups(self, limit=10):
        """List recent backups from Google Drive
        
        Returns:
            List of backup file info
        """
        if not self.service:
            return []
        
        try:
            query = "trunc(createdTime)=trunc(now())" if self.folder_id else None
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime, size)',
                pageSize=limit,
                orderBy='createdTime desc'
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing Google Drive backups: {str(e)}")
            return []


class DropboxBackup:
    """Handle backups to Dropbox"""
    
    def __init__(self, access_token=None):
        """Initialize Dropbox client
        
        Args:
            access_token: Dropbox access token
        """
        if not DROPBOX_AVAILABLE:
            raise ImportError("Dropbox library not installed")
        
        self.dbx = None
        if access_token:
            try:
                self.dbx = dropbox.Dropbox(access_token)
                # Test connection
                self.dbx.users_get_current_account()
            except Exception as e:
                raise Exception(f"Failed to authenticate with Dropbox: {str(e)}")
    
    def upload_backup(self, backup_data, filename):
        """Upload backup file to Dropbox
        
        Args:
            backup_data: File data as bytes
            filename: Name of the file to upload
            
        Returns:
            Tuple of (success, message, path)
        """
        if not self.dbx:
            return False, "Dropbox not configured", None
        
        try:
            dropbox_path = f"/Backups/youth-checkin/{filename}"
            
            # Upload file (will overwrite if exists)
            result = self.dbx.files_upload(
                backup_data,
                dropbox_path,
                autorename=False,
                mode=dropbox.files.WriteMode('overwrite', None)
            )
            
            return True, f"Backup uploaded to Dropbox: {filename}", dropbox_path
        
        except ApiError as e:
            return False, f"Dropbox upload failed: {str(e)}", None
        except Exception as e:
            return False, f"Dropbox upload failed: {str(e)}", None
    
    def list_backups(self, limit=10):
        """List recent backups from Dropbox
        
        Returns:
            List of backup file info
        """
        if not self.dbx:
            return []
        
        try:
            result = self.dbx.files_list_folder('/Backups/youth-checkin')
            files = [
                {
                    'name': entry.name,
                    'path': entry.path_display,
                    'size': entry.size if hasattr(entry, 'size') else 0,
                    'modified': entry.server_modified.isoformat() if hasattr(entry, 'server_modified') else None
                }
                for entry in result.entries
                if isinstance(entry, dropbox.files.FileMetadata)
            ]
            return sorted(files, key=lambda x: x['modified'], reverse=True)[:limit]
        except Exception as e:
            print(f"Error listing Dropbox backups: {str(e)}")
            return []


class OneDriveBackup:
    """Handle backups to OneDrive using Microsoft Graph API"""
    
    def __init__(self, access_token=None):
        """Initialize OneDrive client
        
        Args:
            access_token: OneDrive/Microsoft Graph access token
        """
        self.access_token = access_token
        self.api_base = "https://graph.microsoft.com/v1.0/me/drive"
    
    def upload_backup(self, backup_data, filename):
        """Upload backup file to OneDrive
        
        Args:
            backup_data: File data as bytes
            filename: Name of the file to upload
            
        Returns:
            Tuple of (success, message, file_id)
        """
        if not self.access_token:
            return False, "OneDrive not configured", None
        
        try:
            import requests
            
            # Create or get the Backups folder
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            # Upload file to root of OneDrive (can be modified to use specific folder)
            upload_url = f"{self.api_base}/root:/youth-checkin-backups/{filename}:/content"
            
            response = requests.put(
                upload_url,
                data=backup_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                file_info = response.json()
                return True, f"Backup uploaded to OneDrive: {filename}", file_info.get('id')
            else:
                return False, f"OneDrive upload failed: {response.text}", None
        
        except Exception as e:
            return False, f"OneDrive upload failed: {str(e)}", None
    
    def list_backups(self, limit=10):
        """List recent backups from OneDrive
        
        Returns:
            List of backup file info
        """
        if not self.access_token:
            return []
        
        try:
            import requests
            
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            # List files in backup folder
            list_url = f"{self.api_base}/root:/youth-checkin-backups:/children"
            
            response = requests.get(list_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                files = [
                    {
                        'name': item['name'],
                        'id': item['id'],
                        'size': item.get('size', 0),
                        'modified': item.get('lastModifiedDateTime')
                    }
                    for item in data.get('value', [])
                    if 'file' in item
                ]
                return sorted(files, key=lambda x: x['modified'], reverse=True)[:limit]
            return []
        
        except Exception as e:
            print(f"Error listing OneDrive backups: {str(e)}")
            return []


def create_database_backup(db_path):
    """Create a backup of the entire database
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Tuple of (backup_data, filename)
    """
    try:
        with open(db_path, 'rb') as f:
            backup_data = f.read()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"youth-checkin-db_{timestamp}.db"
        
        return backup_data, filename
    
    except Exception as e:
        raise Exception(f"Failed to create database backup: {str(e)}")


def backup_to_cloud(db_path, google_drive=None, dropbox_client=None, onedrive_token=None):
    """Backup database to all configured cloud services
    
    Args:
        db_path: Path to the SQLite database
        google_drive: GoogleDriveBackup instance (optional)
        dropbox_client: DropboxBackup instance (optional)
        onedrive_token: OneDrive access token (optional)
        
    Returns:
        Dictionary with results for each service
    """
    try:
        backup_data, filename = create_database_backup(db_path)
    except Exception as e:
        return {'error': str(e), 'success': False}
    
    results = {
        'filename': filename,
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'success': False
    }
    
    # Google Drive backup
    if google_drive:
        try:
            success, message, file_id = google_drive.upload_backup(backup_data, filename)
            results['services']['google_drive'] = {
                'success': success,
                'message': message,
                'file_id': file_id
            }
        except Exception as e:
            results['services']['google_drive'] = {
                'success': False,
                'message': str(e)
            }
    
    # Dropbox backup
    if dropbox_client:
        try:
            success, message, path = dropbox_client.upload_backup(backup_data, filename)
            results['services']['dropbox'] = {
                'success': success,
                'message': message,
                'path': path
            }
        except Exception as e:
            results['services']['dropbox'] = {
                'success': False,
                'message': str(e)
            }
    
    # OneDrive backup
    if onedrive_token:
        try:
            od_backup = OneDriveBackup(onedrive_token)
            success, message, file_id = od_backup.upload_backup(backup_data, filename)
            results['services']['onedrive'] = {
                'success': success,
                'message': message,
                'file_id': file_id
            }
        except Exception as e:
            results['services']['onedrive'] = {
                'success': False,
                'message': str(e)
            }
    
    # Mark as success if at least one service succeeded
    results['success'] = any(
        s.get('success', False) 
        for s in results['services'].values()
    )
    
    return results
