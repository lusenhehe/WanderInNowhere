import json, os,base64
from src.utils.logger import logger

class ConfigEncryption:
    # 简单的 XOR 加密示例
    # TODO: 尝试将密钥存储在更安全的位置
    KEY = b'LZNSecretKey' 

    @staticmethod
    def _xor_bytes(data: bytes, key: bytes) -> bytes:
        # XOR 加密/解密
        key_len = len(key)
        return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))

    @classmethod
    def encrypt(cls, data: str) -> str:
        # 1. 编码为字节
        json_bytes = data.encode('utf-8')
        # 2. XOR 加密
        encrypted_bytes = cls._xor_bytes(json_bytes, cls.KEY)
        # 3. Base64 编码以便存储为文本
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    @classmethod
    def decrypt(cls, data: str) -> str:
        try:
            # 1. Base64 解码
            encrypted_bytes = base64.b64decode(data)
            # 2. XOR 解密 (XOR 是对称的)
            decrypted_bytes = cls._xor_bytes(encrypted_bytes, cls.KEY)
            # 3. 解码为字符串
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"解码失败: {e}")
            raise e
def _migrate_config(data, default_config):
    """
    迁移旧版本配置到最新版本的结构。
    :param data: 当前配置数据
    """
    # 目前的最新版本
    CURRENT_VERSION = 1
    
    config_version = data.get('version', 0)
    
    if config_version < CURRENT_VERSION:
        logger.info(f"配置文件(Config)从版本{config_version}到{CURRENT_VERSION}")
        data['version'] = CURRENT_VERSION
        
    # 确保所有默认键存在
    for key, val in default_config.items():
        if key not in data:
            data[key] = val
            
    return data
def load_encrypted_config(path, default_config):
    if not os.path.exists(path):
        return default_config.copy()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        try:
            json_str = ConfigEncryption.decrypt(content)
            data = json.loads(json_str)
        except Exception:
            try:
                data = json.loads(content)
            except:
                logger.error("加载配置失败，既不是加密格式也不是纯JSON格式。")
                try:
                    backup_path = path + ".corrupted"
                    with open(backup_path, 'w', encoding='utf-8') as bf:
                        bf.write(content)
                    logger.info(f"已备份损坏的配置到 {backup_path}")
                    logger.warning(f"配置文件损坏，已重置。原文件备份为: {os.path.basename(backup_path)}")
                except:
                    logger.error("备份损坏的配置文件失败。")
                return default_config.copy()
        
        # 验证数据类型
        if not isinstance(data, dict):
            logger.error("Config data is not a dictionary.")
            return default_config.copy()

        # 迁移配置
        return _migrate_config(data, default_config)

    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return default_config.copy()
def save_encrypted_config(path, config_dict):
    try:
        # 保证版本号存在
        if 'version' not in config_dict:
            config_dict['version'] = 1

        json_str = json.dumps(config_dict, indent=4, ensure_ascii=False)
        encrypted_str = ConfigEncryption.encrypt(json_str)
        
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(encrypted_str)
    except Exception as e:
        logger.error(f"保存配置出错: {e}")
