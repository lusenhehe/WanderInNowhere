import os, json, datetime, hashlib, shutil
from typing import Callable, Optional
from src.utils.logger import logger
from src.Constants.game_constants import EQUIPMENT_SLOTS
from src.Constants.config import SAVES_DIR
from src.utils.business_logic_utils import BusinessLogicUtils
from src.Data import PlayerData, EntityData,GameSave
def ensure_saves_dir():
    os.makedirs(SAVES_DIR, exist_ok=True)
def calculate_checksum(data_dict):
    json_str = json.dumps(data_dict, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
def get_all_saves():
    """
    get_all_saves: 获取所有存档的简要信息列表。
    :return: 存档信息列表
    """
    ensure_saves_dir()
    saves = []
    for filename in os.listdir(SAVES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SAVES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        logger.warning(f"跳过无效存档文件（不是字典类型）: {filename}")
                        continue
                    # 兼容旧存档或确保字段存在
                    saves.append({"filename": filename,"world_name": data.get("world_name", data.get("name", "未知世界")),"player_name": data.get("player_name", "未知角色"),"name": data.get("name", filename.replace(".json", "")),"last_played": data.get("last_played", "未知时间"),"history": data.get("history", []),"summaries": data.get("summaries", []),"status": data.get("status", {}),"location": data.get("location", "未知地点"),"world": data.get("world", {})})
            except Exception as e:
                logger.error(f"存档导入错误，存档名称{filename}: {e}")
    # 按最后游玩时间倒序
    saves.sort(key=lambda x: x["last_played"], reverse=True)
    return saves
def create_new_save_file(world_name, player_name, history, location="废都", magic_density="40%"):
    """创建一个新的存档文件并返回其文件名。
    param world_name: 世界名称
    param player_name: 角色名称
    param history: 初始对话历史
    param location: 初始位置
    param magic_density: 初始魔力密度
    return: 存档文件名
    """
    ensure_saves_dir()
    safe_world_name = "".join([c for c in world_name if c.isalnum() or c in (' ', '_', '-')]).strip()
    if not safe_world_name:
        safe_world_name = "NewWorld"
        
    filename = f"{safe_world_name}_{int(datetime.datetime.now().timestamp())}.json"
    inventory = []
    initial_equipment = {slot: None for slot in EQUIPMENT_SLOTS.keys()}
    # 使用业务逻辑工具解析魔力密度
    try:
        if isinstance(magic_density, str):
            mag_num = BusinessLogicUtils.parse_resource_string(magic_density)[0]
        elif isinstance(magic_density, (int, float)):
            mag_num = int(magic_density)
        else:
            mag_num = 20
    except:
        mag_num = 20

    mp_max = max(10, int(mag_num * 2))
    mp_cur = mp_max

    player_data = PlayerData(
        name=player_name,
        inventory=inventory,
        equipment=initial_equipment,
        money=0,
        location=location,
        status={
            "hp": "100/100",
            "magic": f"{mp_cur}/{mp_max}",
            "magic_concentration": mag_num,
            "mp": mp_cur,
            "mp_max": mp_max,
            "hunger": "100/100",
            "injury": "无",
            "action": "正常"
        }
    )
    
    # 初始世界状态
    world = {
        "time": "第1天 08:00",
        "weather": "晴朗"
    }
    
    game_save = GameSave(
        filename=filename,
        world_name=world_name,
        player_data=player_data,
        history=history,
        world=world,
        entities=[]
    )
    save_game_data(game_save)
    return filename
def save_game_data(game_save: GameSave):
    ensure_saves_dir()
    filepath = os.path.join(SAVES_DIR, game_save.filename)
    # 如果存在现有存档，则备份
    if os.path.exists(filepath):
        try:
            backup_path = filepath + ".bak"
            shutil.copy2(filepath, backup_path)
        except Exception as e:
            logger.warning(f"创建备份失败，存档名称{game_save.filename}: {e}")
    final_data = {}
    # 更新最后游玩时间
    game_save.update_last_played()
    if isinstance(game_save.player_data, PlayerData):
        p_dict = game_save.player_data.to_dict()
        # 处理实体
        entities_data = []
        if game_save.entities:
            for ent in game_save.entities:
                if isinstance(ent, EntityData):
                    entities_data.append(ent.to_dict())
                else:
                    entities_data.append(ent)
        # 修剪历史记录到最多100项以保存（保留最新的）
        # 但确保如果存在系统提示，则保留
        saved_history = game_save.history
        saved_summarized_line = game_save.summarized_line
        
        if len(game_save.history) > 100:
            saved_history = game_save.history[-100:]
            offset = len(game_save.history) - len(saved_history)
            saved_summarized_line = max(0, game_save.summarized_line - offset)
        final_data = {
            "filename": game_save.filename,
            "world_name": game_save.world_name,
            "player_name": game_save.player_data.name,
            "name": game_save.world_name,
            "last_played": game_save.last_played,
            "history": saved_history,
            "summaries": game_save.summaries,
            "summarized_line": saved_summarized_line,
            "status": game_save.player_data.status,
            "inventory": p_dict["inventory"],
            "money": game_save.player_data.money,
            "equipment": p_dict["equipment"],
            "world": game_save.world if game_save.world else {"time": "未知", "weather": "未知"},
            "location": game_save.player_data.location,
            "entities": entities_data,
            "quests": p_dict.get("quests", []),
            "skills": p_dict.get("skills", [])
        }
    else:
        logger.error("不合法的玩家数据类型，无法保存存档。")
        return
    final_data['checksum'] = calculate_checksum(final_data)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"存档保存失败，存档名称{game_save.filename}: {e}")
def load_save_data(filename,*,confirm_load_backup: Optional[Callable[[str, str], bool]] = None,on_info: Optional[Callable[[str, str], None]] = None,on_warning: Optional[Callable[[str, str], None]] = None,on_error: Optional[Callable[[str, str], None]] = None,):
    filepath = os.path.join(SAVES_DIR, filename)
    if not os.path.exists(filepath):
        logger.error(f"存档文件未找到: {filename}")
        if on_error:
            on_error("加载失败", "存档文件不存在")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 如果存在校验和，则验证
        if 'checksum' in data:
            stored_checksum = data['checksum']
            # 从数据中移除校验和以计算内容的哈希
            data_copy = data.copy()
            del data_copy['checksum']
            calculated_checksum = calculate_checksum(data_copy)
            if stored_checksum != calculated_checksum:
                logger.warning(f"存档校验和不匹配: {filename}")
                use_backup = False
                if confirm_load_backup is not None:
                    use_backup = bool(confirm_load_backup("数据校验警告","存档数据校验失败，文件可能已损坏或被篡改。\n是否尝试加载备份？",))
                else:
                    if on_warning:
                        on_warning("数据校验警告","存档数据校验失败，文件可能已损坏或被篡改。\n未提供确认回调，将继续尝试加载当前存档。",)
                if use_backup:
                    backup_path = filepath + ".bak"
                    if os.path.exists(backup_path):
                        try:
                            with open(backup_path, 'r', encoding='utf-8') as bf:
                                backup_data = json.load(bf)
                                if on_info:
                                    on_info("备份加载", "已成功加载备份存档。")
                                return backup_data
                        except Exception as be:
                            if on_error:
                                on_error("备份加载失败", f"无法加载备份文件: {be}")
                            return None
                    else:
                        if on_warning:
                            on_warning("无备份", "未找到备份文件。")
        return data
    except json.JSONDecodeError:
        logger.error(f"JSON 解码错误: {filename}")
        if on_error:
            on_error("加载失败", "存档文件格式错误")
        return None
    except Exception as e:
        logger.error(f"加载存档错误，存档名称{filename}: {e}")
        if on_error:
            on_error("加载失败", f"无法读取存档: {e}")
        return None
def delete_save_file(filename):
    filepath = os.path.join(SAVES_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"删除存档文件: {filename}")