import csv
import os
from src.AI.prompts import load_prompts
from src.utils.logger import logger
def load_skills_to_string(filepath="src/Data/skills.csv"):
    """
    读取技能数据并将其转换为适合 AI 阅读的字符串格式。
    优先从 prompts.json 读取，如果不存在则尝试读取 skills.csv。
    """
    skill_str = "【已知技能列表（仅供参考，可以自己生成）】\n"
    # 1.尝试从 prompts.json 读取
    prompts_data = load_prompts()
    skills_json = prompts_data.get("skills", [])
    if skills_json:
        for skill in skills_json:
            name = skill.get('name', '未知')
            element = skill.get('element', '无')
            cost = skill.get('cost', '0')
            density = skill.get('density', '无')
            desc = skill.get('description', '无')
            rarity = skill.get('rarity', '普通')
            preact = skill.get('preacttime', '1.0')
            finish = skill.get('finishtime', '1.0')
            skill_str += f"- {name}: [{element}] {rarity} 消耗:{cost}, 浓度:{density}, 前摇:{preact}s, 后摇:{finish}s。效果: {desc}\n"
        return skill_str

    # 2. 尝试从 skills.csv 读取
    if not os.path.exists(filepath):
        return "暂无预设技能数据。"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name', '未知')
                element = row.get('element', '无')
                cost = row.get('cost', '0')
                density = row.get('density', '无')
                desc = row.get('description', '无')
                rarity = row.get('rarity', '普通')
                preact = row.get('preacttime', '1.0')
                finish = row.get('finishtime', '1.0')
                
                skill_str += f"- {name}: [{element}] {rarity} 消耗:{cost}, 浓度:{density}, 前摇:{preact}s, 后摇:{finish}s。效果: {desc}\n"
    except Exception as e:
        logger.error(f"读取技能数据出错: {e}")
        return "技能数据读取出错。"
    return skill_str