import re
import ast
from src.utils.logger import logger
from src.AI.CommandHandler import (
    StatusCommandHandler,
    WorldCommandHandler,
    InventoryCommandHandler,
    EntityCommandHandler,
    QuestCommandHandler,
    SkillCommandHandler
)


# Tolerant state-block patterns to handle small AI formatting mistakes, such as:
# </STATE_END>, <\STATE_END>, <STATE_END/>, mixed case and extra spaces.
STATE_BLOCK_PATTERN = re.compile(
    r'<\s*STATE_START\s*>(.*?)<\s*[\\/]*\s*STATE_END\s*(?:[\\/]*)\s*>',
    re.DOTALL | re.IGNORECASE,
)
STATE_START_PATTERN = re.compile(r'<\s*STATE_START\s*>', re.IGNORECASE)


def extract_state_block(full_response: str) -> str | None:
    """Extract the content inside <STATE_START> ... <STATE_END> if present."""
    if not full_response:
        return None
    match = STATE_BLOCK_PATTERN.search(full_response)
    if not match:
        return None
    return match.group(1).strip()


def strip_state_block(content: str) -> str:
    """Remove state blocks from assistant-visible text.

    If a start tag exists without a valid end tag, strip everything from
    the start tag to the end of text to avoid leaking control directives.
    """
    text = str(content or "")
    text = STATE_BLOCK_PATTERN.sub("", text)
    start_match = STATE_START_PATTERN.search(text)
    if start_match:
        text = text[:start_match.start()]
    return text.strip()


class AICommandExecutor:
    COMMAND_HANDLERS = {
        "SetHp": StatusCommandHandler,
        "SetMagic": StatusCommandHandler,
        "SetHunger": StatusCommandHandler,
        "SetInjury": StatusCommandHandler,
        "RemoveInjury": StatusCommandHandler,
        "SetAction": StatusCommandHandler,
        "SetMoney": StatusCommandHandler,
        
        "SetLocation": WorldCommandHandler,
        "SetTime": WorldCommandHandler,
        "SetWeather": WorldCommandHandler,
        
        "AddItem": InventoryCommandHandler,
        "RemoveItem": InventoryCommandHandler,
        "EquipItem": InventoryCommandHandler,
        "UnequipItem": InventoryCommandHandler,
        
        "UpdateEntity": EntityCommandHandler,
        
        "AddQuest": QuestCommandHandler,
        "UpdateQuest": QuestCommandHandler,
        "CompleteQuest": QuestCommandHandler,
        
        "AddSkill": SkillCommandHandler,
        "RemoveSkill": SkillCommandHandler,
    }

    @staticmethod
    def execute(full_response, game):
        """
        解析 AI 的完整回复，并直接在 game 对象上执行指令。
        
        该方法会查找回复中的 <STATE_START>...<STATE_END> 块，
        解析其中的指令（如 SetHp(100)），并分发给相应的 CommandHandler 执行。
        
        :param full_response: AI 返回的完整文本字符串。
        :param game: 游戏主对象 (GameScreen 实例)，用于访问 player_data 等。
        :return: None
        """
        instr_block = extract_state_block(full_response)
        if not instr_block:
            return

        lines = instr_block.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            match = re.match(r'(\w+)\((.*)\)', line)
            if not match: continue
            
            cmd, args_str = match.groups()
            try:
                try:
                    args = ast.literal_eval(f"({args_str},)")
                except (ValueError, SyntaxError):
                    if cmd in AICommandExecutor.COMMAND_HANDLERS.keys():
                         args = (args_str,)
                    else:
                         continue
            except Exception:
                continue
            try:
                handler_class = AICommandExecutor.COMMAND_HANDLERS.get(cmd)
                if handler_class:
                    handler_class.handle(cmd, args, game)
                else:
                    logger.warning(f"未知指令: {cmd}")

            except IndexError:
                pass
            except Exception as e:
                logger.error(f"执行指令时出错 {cmd}: {e}")