"""
文件处理工具类
提供文件操作相关的工具方法
"""

import csv
import hashlib
import mimetypes
import os
import shutil
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from werkzeug.utils import secure_filename


class FileUtil:
    """文件工具类"""

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {
        'csv', 'xlsx', 'xls', 'json', 'txt',
        'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'
    }

    # 文件大小限制 (bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """检查文件是否允许上传"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUtil.ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """获取文件扩展名"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    @staticmethod
    def secure_filename(filename: str) -> str:
        """生成安全的文件名"""
        return secure_filename(filename)

    @staticmethod
    def generate_unique_filename(filename: str, upload_dir: str) -> str:
        """生成唯一文件名"""
        import uuid
        
        name, ext = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{name}_{unique_id}{ext}"
        
        # 确保文件名不冲突
        counter = 1
        while os.path.exists(os.path.join(upload_dir, new_filename)):
            new_filename = f"{name}_{unique_id}_{counter}{ext}"
            counter += 1
        
        return new_filename

    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """计算文件哈希值"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f}PB"

    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """获取文件MIME类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    @staticmethod
    def ensure_dir(directory: str) -> None:
        """确保目录存在"""
        Path(directory).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_csv_file(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """读取CSV文件"""
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            # 处理NaN值
            df = df.fillna('')
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"读取CSV文件失败: {str(e)}")

    @staticmethod
    def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """读取Excel文件"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # 处理NaN值
            df = df.fillna('')
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"读取Excel文件失败: {str(e)}")

    @staticmethod
    def read_json_file(file_path: str, encoding: str = 'utf-8') -> Union[Dict, List]:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                import json
                return json.load(f)
        except Exception as e:
            raise ValueError(f"读取JSON文件失败: {str(e)}")

    @staticmethod
    def write_csv_file(data: List[Dict[str, Any]], file_path: str, encoding: str = 'utf-8') -> None:
        """写入CSV文件"""
        try:
            if not data:
                return
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding=encoding)
        except Exception as e:
            raise ValueError(f"写入CSV文件失败: {str(e)}")

    @staticmethod
    def write_excel_file(data: List[Dict[str, Any]], file_path: str, sheet_name: str = 'Sheet1') -> None:
        """写入Excel文件"""
        try:
            if not data:
                return
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
        except Exception as e:
            raise ValueError(f"写入Excel文件失败: {str(e)}")

    @staticmethod
    def write_json_file(data: Union[Dict, List], file_path: str, encoding: str = 'utf-8') -> None:
        """写入JSON文件"""
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                import json
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"写入JSON文件失败: {str(e)}")

    @staticmethod
    def copy_file(src: str, dst: str) -> None:
        """复制文件"""
        try:
            # 确保目标目录存在
            FileUtil.ensure_dir(os.path.dirname(dst))
            shutil.copy2(src, dst)
        except Exception as e:
            raise ValueError(f"复制文件失败: {str(e)}")

    @staticmethod
    def move_file(src: str, dst: str) -> None:
        """移动文件"""
        try:
            # 确保目标目录存在
            FileUtil.ensure_dir(os.path.dirname(dst))
            shutil.move(src, dst)
        except Exception as e:
            raise ValueError(f"移动文件失败: {str(e)}")

    @staticmethod
    def delete_file(file_path: str) -> None:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise ValueError(f"删除文件失败: {str(e)}")

    @staticmethod
    def create_temp_file(suffix: str = '', prefix: str = 'tmp') -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False)
        temp_file.close()
        return temp_file.name

    @staticmethod
    def cleanup_temp_files(temp_files: List[str]) -> None:
        """清理临时文件"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # 忽略清理失败

    @staticmethod
    def validate_file_content(file_path: str, expected_format: str) -> Tuple[bool, str]:
        """验证文件内容格式"""
        try:
            if expected_format.lower() == 'csv':
                # 验证CSV格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    next(csv_reader)  # 读取第一行
                return True, "文件格式正确"
            
            elif expected_format.lower() in ['xlsx', 'xls']:
                # 验证Excel格式
                pd.read_excel(file_path, nrows=1)
                return True, "文件格式正确"
            
            elif expected_format.lower() == 'json':
                # 验证JSON格式
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return True, "文件格式正确"
            
            else:
                return False, f"不支持的文件格式: {expected_format}"
                
        except Exception as e:
            return False, f"文件格式验证失败: {str(e)}"

    @staticmethod
    def compress_file(file_path: str, output_path: str = None) -> str:
        """压缩文件"""
        import gzip
        
        if output_path is None:
            output_path = file_path + '.gz'
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return output_path
        except Exception as e:
            raise ValueError(f"压缩文件失败: {str(e)}")

    @staticmethod
    def decompress_file(compressed_path: str, output_path: str = None) -> str:
        """解压文件"""
        import gzip
        
        if output_path is None:
            output_path = compressed_path.replace('.gz', '')
        
        try:
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return output_path
        except Exception as e:
            raise ValueError(f"解压文件失败: {str(e)}")

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """获取文件详细信息"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'size_formatted': FileUtil.format_file_size(stat.st_size),
                'mime_type': FileUtil.get_mime_type(file_path),
                'extension': FileUtil.get_file_extension(file_path),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'hash_md5': FileUtil.calculate_file_hash(file_path, 'md5'),
            }
        except Exception as e:
            raise ValueError(f"获取文件信息失败: {str(e)}")

    @staticmethod
    def batch_process_files(file_paths: List[str], processor_func, batch_size: int = 10) -> List[Any]:
        """批量处理文件"""
        results = []
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            for file_path in batch:
                try:
                    result = processor_func(file_path)
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e), 'file': file_path})
        return results
