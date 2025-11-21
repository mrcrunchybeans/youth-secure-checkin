#!/usr/bin/env python3
"""
Backup Manager for Youth Secure Check-in
Handles automatic backup rotation with retention policy:
- Keep last 3 backups (recent/daily)
- Keep 1 weekly backup (7+ days old)
- Keep 1 monthly backup (30+ days old)
"""

import os
import sqlite3
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import tempfile


class BackupManager:
    def __init__(self, db_path, backup_dir='data/backups', uploads_dir='uploads', static_uploads_dir='static/uploads'):
        """
        Initialize backup manager
        
        Args:
            db_path: Path to SQLite database
            backup_dir: Directory to store backups
            uploads_dir: Path to uploads directory (if exists)
            static_uploads_dir: Path to static/uploads directory (if exists)
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.uploads_dir = Path(uploads_dir)
        self.static_uploads_dir = Path(static_uploads_dir)
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, description='Automatic backup'):
        """
        Create a backup zip file with database and uploads
        
        Args:
            description: Optional description for the backup
            
        Returns:
            Path to created backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = self.backup_dir / backup_filename
        
        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add database
            if self.db_path.exists():
                zf.write(self.db_path, arcname='checkin.db')
            
            # Add data directory contents (if any)
            data_dir = self.db_path.parent
            if data_dir.exists() and data_dir.name == 'data':
                for root, dirs, files in os.walk(data_dir):
                    # Skip the backups directory itself
                    if 'backups' in Path(root).parts:
                        continue
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(data_dir.parent)
                        zf.write(file_path, arcname=arcname)
            
            # Add uploads directory
            if self.uploads_dir.exists():
                for root, dirs, files in os.walk(self.uploads_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.uploads_dir.parent)
                        zf.write(file_path, arcname=arcname)
            
            # Add static/uploads directory
            if self.static_uploads_dir.exists():
                for root, dirs, files in os.walk(self.static_uploads_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.static_uploads_dir.parent.parent)
                        zf.write(file_path, arcname=arcname)
            
            # Add metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'description': description,
                'version': '1.0'
            }
            zf.writestr('backup_metadata.txt', str(metadata))
        
        return backup_path
    
    def list_backups(self):
        """
        List all available backups with metadata
        
        Returns:
            List of dicts with backup info (filename, size, date, age_days)
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('backup_*.zip'), reverse=True):
            stat = backup_file.stat()
            created_time = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - created_time).days
            
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': created_time,
                'created_str': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'age_days': age_days
            })
        
        return backups
    
    def rotate_backups(self):
        """
        Rotate backups according to retention policy:
        - Keep last 3 backups
        - Keep 1 weekly backup (7-30 days old)
        - Keep 1 monthly backup (30+ days old)
        
        Returns:
            Tuple of (kept_count, deleted_count)
        """
        backups = self.list_backups()
        
        if not backups:
            return 0, 0
        
        # Categorize backups
        recent = []      # Last 3 backups
        weekly = []      # 7-30 days old
        monthly = []     # 30+ days old
        
        for backup in backups:
            age = backup['age_days']
            if age < 7:
                recent.append(backup)
            elif age < 30:
                weekly.append(backup)
            else:
                monthly.append(backup)
        
        # Determine which to keep
        to_keep = set()
        
        # Keep last 3 recent backups
        for backup in recent[:3]:
            to_keep.add(backup['filename'])
        
        # Keep 1 weekly backup (oldest in weekly range)
        if weekly:
            to_keep.add(weekly[-1]['filename'])
        
        # Keep 1 monthly backup (oldest available)
        if monthly:
            to_keep.add(monthly[-1]['filename'])
        
        # Delete backups not in keep list
        deleted_count = 0
        for backup in backups:
            if backup['filename'] not in to_keep:
                Path(backup['path']).unlink()
                deleted_count += 1
        
        kept_count = len(to_keep)
        return kept_count, deleted_count
    
    def restore_backup(self, backup_filename):
        """
        Restore from a backup file
        
        Args:
            backup_filename: Name of backup file to restore
            
        Returns:
            Tuple of (success, message)
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return False, f"Backup file not found: {backup_filename}"
        
        try:
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as tmpdir:
                # Extract backup
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    zf.extractall(tmpdir)
                
                tmpdir_path = Path(tmpdir)
                
                # Backup current database before restoring
                if self.db_path.exists():
                    backup_current = self.db_path.parent / f'checkin_before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                    shutil.copy2(self.db_path, backup_current)
                
                # Restore database
                db_backup = tmpdir_path / 'checkin.db'
                if db_backup.exists():
                    shutil.copy2(db_backup, self.db_path)
                
                # Restore data directory
                data_backup = tmpdir_path / 'data'
                if data_backup.exists():
                    data_dir = self.db_path.parent
                    for item in data_backup.iterdir():
                        if item.name == 'backups':
                            continue  # Don't restore old backups
                        dest = data_dir / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        elif item.is_dir():
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(item, dest)
                
                # Restore uploads
                uploads_backup = tmpdir_path / 'uploads'
                if uploads_backup.exists():
                    if self.uploads_dir.exists():
                        shutil.rmtree(self.uploads_dir)
                    shutil.copytree(uploads_backup, self.uploads_dir)
                
                # Restore static/uploads
                static_uploads_backup = tmpdir_path / 'static' / 'uploads'
                if static_uploads_backup.exists():
                    if self.static_uploads_dir.exists():
                        shutil.rmtree(self.static_uploads_dir)
                    shutil.copytree(static_uploads_backup, self.static_uploads_dir)
            
            return True, f"Successfully restored from {backup_filename}"
        
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def delete_backup(self, backup_filename):
        """
        Delete a specific backup file
        
        Args:
            backup_filename: Name of backup file to delete
            
        Returns:
            Tuple of (success, message)
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return False, f"Backup file not found: {backup_filename}"
        
        try:
            backup_path.unlink()
            return True, f"Deleted backup: {backup_filename}"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def get_backup_summary(self):
        """
        Get summary of backup status
        
        Returns:
            Dict with backup statistics
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size_mb': 0,
                'newest_backup': None,
                'oldest_backup': None
            }
        
        total_size = sum(b['size'] for b in backups)
        
        return {
            'total_backups': len(backups),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'newest_backup': backups[0],
            'oldest_backup': backups[-1]
        }


def main():
    """Test backup manager"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python backup_manager.py <command>")
        print("Commands: create, list, rotate, summary")
        sys.exit(1)
    
    db_path = os.getenv('DATABASE_PATH', 'data/checkin.db')
    manager = BackupManager(db_path)
    
    command = sys.argv[1]
    
    if command == 'create':
        backup_path = manager.create_backup('Manual backup')
        print(f"Created backup: {backup_path}")
    
    elif command == 'list':
        backups = manager.list_backups()
        print(f"\nFound {len(backups)} backups:")
        for b in backups:
            print(f"  {b['filename']} - {b['size_mb']}MB - {b['created_str']} ({b['age_days']} days old)")
    
    elif command == 'rotate':
        kept, deleted = manager.rotate_backups()
        print(f"Rotation complete: kept {kept}, deleted {deleted}")
    
    elif command == 'summary':
        summary = manager.get_backup_summary()
        print("\nBackup Summary:")
        print(f"  Total backups: {summary['total_backups']}")
        print(f"  Total size: {summary['total_size_mb']}MB")
        if summary['newest_backup']:
            print(f"  Newest: {summary['newest_backup']['created_str']}")
            print(f"  Oldest: {summary['oldest_backup']['created_str']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
