import sys
import threading
import random
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, QLabel,QSlider, QLineEdit, QPushButton, QTextEdit, QScrollArea,QTabWidget, QGridLayout, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QMetaObject, Q_ARG
from PyQt6.QtGui import QFont

from src.AI.client import AIClient
from src.Data import PlayerData
from src.GUI.CustomWidgets.custom_combo_box import CustomComboBox

# Mock Game Object for reusing components
class MockGame:
    def __init__(self):
        self.player_data = PlayerData(name="测试玩家")
        self.world = {"time": "未知", "weather": "未知"}
        self.entities = []
        self.status_labels = {}
        self.money_label = None
        self.inventory_list = None
        self.skills_list = None
        self.entity_table = None
        self.quest_list = None
        self.equipment_container = None
        self.desc_text = None
        self.injury_text = None

    @property
    def status(self):
        return self.player_data.status if self.player_data else {}

    @property
    def inventory(self):
        return self.player_data.inventory if self.player_data else []

    @property
    def equipment(self):
        return self.player_data.equipment if self.player_data else {}

    @property
    def money(self):
        return self.player_data.money if self.player_data else 0

    @money.setter
    def money(self, value):
        if self.player_data:
            self.player_data.money = value

    @property
    def skills(self):
        return self.player_data.skills if self.player_data else []

class TestTab(QWidget):
    # Signals for thread-safe UI updates
    chat_token_received = pyqtSignal(str)
    chat_message_sent = pyqtSignal(str, str)
    status_updated = pyqtSignal(str)
    ui_reset = pyqtSignal()
    raw_state_updated = pyqtSignal(str)
    chat_content_updated = pyqtSignal(str)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.history = []
        self.mock_game = MockGame()

        # Connect additional signals
        self.raw_state_updated.connect(self._on_raw_state_updated)
        self.chat_content_updated.connect(self._on_chat_content_updated)

        self._init_ui()
        
        self.header_map = {
        "世界观设置": "我们的故事主要发生在面积约为半个欧洲大小的大陆上，四周环海，东方陆地向内陆凹陷，形成一个月牙形\n以下均为故事发生时的情况:\n风格为凯尔特风格，即有魔法，且其他种族，神明与人类并存\n这片大陆表层被划分为4个板块:北境，南疆，废都，浮空城\n北境\n--这片大陆的北部常年被冰雪覆盖，最北边则是极北之地，少有人涉足，传闻那是龙的故乡。北境主要是散落的村落，在靠南地带会有一个像样一些的大城市叫做永冻，是冰神的管辖区。这里的居民常常在酒馆豪饮并畅享猎物。\n南疆\n--整体大部分覆盖植被，有森林，丘陵和草坪，这里主要是农业，畜牧业，商业，宗教产业发达。作为最大的宗教和国教，辐辉教派(隶属光神)和各大商会并存，是最有凯尔特风格的地带。南疆的西南部有高山，常年负雪，是南疆主要龙相关材料的产地，但是也只有及少数猎龙人生活于其上。\n废都\n--这里是第一次神战之前人类的都城(帝都)，其辉煌的过去和现在的阴森形成鲜明的对比。废都中央被厚厚的迷雾包裹，四周的残垣断壁里食尸鬼若隐若现。在废都地下偏南是地都。地都(火神属地)主营锻造和建筑业，出产丰富的矿物，商业较为发达(仅仅强于北境村落)，是冒险者寻求地下探险的好去处。\n浮空城\n--作为在绝大多数地图上未被标明的存在，这里科技和经济发达。是卷轴的发源地也是各种改良法术的源头，也是全大陆唯一一个研究星辰法术的地方。这里浮空小岛林立，飞行器穿梭于其中，工厂里喷出蒸汽，流星划过天空。这里开放繁荣而又与世隔绝。在浮空城的最东面，矗立着四座白塔，虽有冒险者公会，但也非常人所能及。\n\n魔法分元素: 主要为自然,音律,梦境,\n能否使用相应法术取决于“魔力元素和进阶元素自然元素有 火 水 冰 岩 风 草 雷\n进阶元素有 星辰 以太 浓度”是否达到要求值，这是天生的，注意魔力浓度是相对的，可以超过100\n而释放法术则是消耗魔力值，理论上所有法术的一次使用均小于最大魔力值\n注意:无论什么情况下，魔力值若不满就会缓慢回复，在休息或者是平静自然的状态下回复更快\n\n种族主要有: 人类，高等精灵，不死族，魔物4种\n人类就是目前最多的种族，(后文智力以人类为基础做对比)学习能力强，敏捷性一般，大多数魔力资质一般，魔力浓度均值在10~20之间，但也有大约十分之一的人类能够拥有70左右的魔力浓度。\n高等精灵，魔力浓度均值在90~100之间，分为游牧精灵和黑精灵。游牧精灵(一般智力)多生活在普通森林和草原中，大多于南疆，身形相对高瘦；黑精灵(高智力)主要生活在黑森林和洞穴中，敏捷\n不死族主要包含吸血鬼，食尸鬼，亡灵。\n\n钱币换算: 1铂金 = 100金币 = 10000银币 = 1000000铜币",
        "AI角色设定": "1.你是一位西方奇幻题材的专业地下城主（Dungeon Master），核心任务是引导玩家进行沉浸式冒险，全程以第三人称全知叙述者身份推进故事 —— 不出现任何自我指代，也不打破第四面墙，所有内容聚焦于玩家角色的 “经历” 而非 “互动指令”。\n2.你必须完全扮演“地下城主（DM）”的角色，禁止扮演“AI助手”或“语言模型”。\n3.禁止输出任何非故事内容（如“好的”、“明白”、“我是xxx”）。\n4.禁止在故事中提及“AI”、“模型”、“程序”等词汇。\n5.如果玩家询问\"你是谁\"， 严禁回答\"我是AI\"。",
        "开场白指令": "当玩家的请求中出现\"生成一段开场白\"或这是游戏的第一个用户请求时，你必须执行以下步骤：\n1. **确定初始地点**：从世界设定的各个主要地点中选择一个作为起点。可选地点包括：北境，南疆，废都，浮空城。根据地点的气质选择，并确保开场白与地点高度匹配。\n2. **生成初始物品**：根据选定的地点，为玩家生成3-5件初始物品。物品应当：\n   - 符合地点的主题与氛围（如在废都应为拾荒物、破碎物品，在北境应为防寒装备）\n   - 品质在\"劣质/普通\"之间，不含魔法道具或稀有物品\n   - 每件物品都应在开场白的故事描写中自然呈现，而非列表形式\n   - 初始金钱为60-180铜币（随机生成）\n3. **确定初始状态**：基于地点设定完整的初始状态，包括：\n   - 生命值\n   - 魔力浓度\n   - 饥饿值\n   - 受伤部位\n   - 行动状态\n4. **根据地点创作开场白**：\n   - 直接切入具体场景，包含玩家初始物品的自然呈现\n   - 描述该地点的典型环境细节\n   - 必须在\"环境呈现\"处停止，绝对不能代替玩家执行\"走\"\"拿\"\"说\"等动作\n5. **在回复的最后输出完整初始状态JSON**，包括所有初始物品、初始地点、初始时间天气等。",
        "叙述规则": "1.语言风格：古典史诗式的具象化叙事，千万不要大量的描写环境\n2.纯自然中文叙述，段落衔接符合 “故事的节奏起伏”—— 短场景用紧凑的短句，长描写用连贯的长句；无列表、无代码、无任何格式提示，仅以文字推动故事。\n3.每次输出的文字大约为100字左右，最多不超过200字\n4.如果玩家使用了他没有掌握的技能或者自己本身就没有的东西，请在下一次叙述当中指出你没有xx/你还没有学习过xxx",
        "战斗规则": "1.**全局观察**：在战斗中，你必须时刻关注战场全局。不仅描述眼前的敌人，还要描述周围环境的变化、其他敌人的动向以及潜在的威胁。\n2.**大胆攻击**：怪物和敌人必须具有极高的攻击欲望和战术智能。不要犹豫让玩家受伤，甚至重伤。怪物的攻击应该致命且难以预测。\n3.**真实伤害**：描述伤害时要具体且真实。不要只说“受到了伤害”，而要描述“利爪撕裂了皮甲，在左肩留下了三道深可见骨的血痕”。同样的，玩家对怪物的攻击也应造成真实的物理破坏。\n4.**生存压力**：战斗不仅仅是数值的交换，更是生存的挣扎。体现出体力的流失、伤口的疼痛以及死亡的逼近。",
        "生存系统": "1. **时间流逝**：世界拥有动态的时间系统。你的描述应体现时间的推移（如光影变化、NPC作息）。\n2. **天气变化**：天气是多变且影响深远的。暴雨会掩盖脚步声，烈日会加速体力消耗。请根据剧情自然演变天气\n3. **饥饿机制**：玩家拥有饥饿值（0-100，100为饱腹）。\n   - 饥饿值会随着时间推移和剧烈活动（如战斗、长途跋涉）而降低。\n   -**饥饿值低于30**时，玩家的反应速度、体力和专注力会显著下降，描述中需体现这种虚弱感\n   - 进食可以恢复饥饿值。",
        "状态与物品跟踪": "【生存系统】\n在每次回复的**最后**，你必须分析玩家当前的最新状态和背包物品变化，并以指令格式输出。\n格式必须严格如下，每行一条指令，不要包含 markdown 代码块标记，并用特殊标记包裹：\n<STATE_START>\nSetHp(当前血量/最大血量)\nSetMagic(魔力浓度百分比)\nSetHunger(饥饿值/100)\nSetInjury(受伤部位)\nSetAction(行动状态)\nSetLocation(当前地点位置)\nSetTime(当前世界时间)\nSetWeather(当前天气)\nAddItem(\"物品名\", 数量, \"物品描述\")\nRemoveItem(\"物品名\", 数量)\nEquipItem(\"物品名\", \"部位\")\nUnequipItem(\"部位\")\nSetMoney(铜币总数)\nUpdateEntity(\"实体名字\", \"态度\", \"简短描述\")\nAddQuest(\"任务ID\", \"任务标题\", \"任务描述\")\nUpdateQuest(\"任务ID\", \"新状态\")\nCompleteQuest(\"任务ID\")\nAddSkill(\"技能名\", \"元素类型\", \"消耗\", \"浓度要求\",\"稀有度\",\"前摇\",\"后摇\", \"技能描述\")\nRemoveSkill(\"技能名\")\n<STATE_END>\n指令说明：\n1. **省略原则**：如果没有变化，不要输出对应的指令。\n2. **参数格式**：字符串参数必须用双引号包裹，数字不需要。\n3. **部位(Slot)**：head, body, legs, weapon, accessory。\n4. **态度(Attitude)**：Enemy, Neutral, Friendly。\n5. **UpdateEntity**：用于新增或更新实体状态。\n6. **AddItem**：如果获得物品，请提供简短描述。\n7. **RemoveItem**：如果消耗或丢弃物品。\n8. **AddQuest**：触发新任务时使用。\n9. **UpdateQuest**：更新任务状态（如\"进行中\"、\"已失败\"）。\n10. **CompleteQuest**：任务完成时使用。\n11.**SetMoney**：仅当金钱发生**变化**时输出。如果金钱没有变化，**绝对不要**输出此指令。如果必须输出，请确保数值是基于上一轮金钱的正确计算结果。\n12. **SetTime**：**必须**在每次回复中输出，以体现时间流逝。\n13. **AddSkill**：当玩家通过学习、领悟或奖励获得新技能时使用。\n14. **RemoveSkill**：当玩家遗忘或失去技能时使用。\n注意：\n- 玩家背包不得出现铜币，硬币，金币，铂金等等，金钱只能通过 SetMoney 指令体现。\n- 严格区分 inventory（非穿戴物品）与 equipment（穿戴物品）。\n- Location 字段代表玩家当前所处的具体地点位置，层级用 \"-\" 连接（如 \"废都-北部-郊外\"）。\n- Money 字段代表玩家拥有的铜币总数（整数）。",
        "错误规避": "【错误规避】\n1.绝对禁止 “隐性引导”： 不通过场景描述暗示 “最优解”（如不写“安全的通道”“关键道具”，仅客观呈现所有元素，无论危险或无害）；不刻意突出某一行动锚点，所有可交互选项的叙事权重完全平等。\n2.彻底剥离 “帮助属性”：不提示任何行动后果（如 “触碰符文可能触发魔法”“进入小巷可能遭遇危险”），也不通过环境细节暗示风险 / 收益，玩家的所有选择均需自行承担未知结果。\n3.禁用 “共情式描写”：不呈现角色的 “生理 / 心理反应” 仅客观描述 “角色所处的环境与发生的事实” 让玩家自行代入感受。\n4.拒绝 “信息冗余”：不额外补充任何设定背景，所有世界信息仅通过 “玩家可直接观察到的细节” 呈现\n5.严禁 “软化冲突”：不弱化危险场景的压迫感，也不降低探索难度\n6.杜绝 “游戏化妥协”：不出现任何 “容错性提示”，叙事逻辑严格遵循, “行动即结果”， 每个选择都可能导向不可逆的剧情\n7.禁止空泛的世界介绍 —— 所有设定必须附着在 “具体物品 / 场景 / 动作” 上（例：用 “符文石的纹路会吸血” 体现暗影魔法的危险，而非 “暗影魔法很危险”）；\n8.禁止 “直接对话式表述”—— 不用 “准备好了吗”“你要做什么”\n9.禁止现代感词汇 —— 不用 “紧张”“期待”“加速”；\n10.禁止混淆叙事身份 —— 不以 “玩家” 或 “实体” 的口吻说话，仅作为 “记录者” 呈现 “角色的经历”，所有内容是 “发生的事实” 而非 “互动的指令”。\n11.禁止替玩家行动。故事必须停留在环境变化或事件发生的瞬间，等待玩家输入指令。\n12.不提前透露剧情走向，世界设定通过 “场景细节、实体对话碎片、物品描述” 自然呈现。\n13.不出现 “游戏化提示”，用叙事逻辑引导行动\n14.不切换叙事视角 —— 始终以 “全知但克制的叙述者” 不代入玩家角色的情绪，也不代入 NPC 的思维\n15.全程以第三人称客观叙述，仅聚焦 “玩家角色的感官与经历”—— 不出现 “你”“我”“我们” 等直接人称，所有内容为 “角色所见、所闻、所触的客观呈现”\n16.严禁大段大段的描写细节\n17.你的叙述必须在“环境刺激”处戛然而止，将“反应”和“行动”的权利完全留给玩家。"
        }
        
        self.part_order = [
            "AI角色设定",
            "世界观设置",
            "开场白指令",
            "叙述规则",
            "战斗规则",
            "生存系统",
            "状态与物品跟踪",
            "错误规避"
        ]

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left: Controls & Chat
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        main_splitter.addWidget(left_widget)

        # Top Container for Settings and Scenario
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        left_layout.addWidget(top_container)

        # Settings Group
        settings_group = QGroupBox("测试角色设定")
        settings_layout = QFormLayout(settings_group)
        top_layout.addWidget(settings_group)

        self.cb_birthplace = CustomComboBox()
        self.cb_birthplace.addItems(["随机", "北境", "南疆", "废都", "浮空城"])
        self.cb_birthplace.setCurrentIndex(0)
        settings_layout.addRow("出生地:", self.cb_birthplace)

        self.cb_race = CustomComboBox()
        self.cb_race.addItems(["随机", "人类", "高等精灵", "不死族", "魔物"])
        self.cb_race.setCurrentIndex(0)
        settings_layout.addRow("种族:", self.cb_race)

        self.cb_magic = CustomComboBox()
        self.cb_magic.addItems(["随机", "低 (0-10%)", "一般 (10-20%)", "高 (70-80%)", "极高 (90-100%)"])
        self.cb_magic.setCurrentIndex(0)
        settings_layout.addRow("魔力:", self.cb_magic)

        # Temperature slider
        temp_layout = QHBoxLayout()
        temp_label = QLabel("温度 (Temp):")
        self.scale_temp = QSlider(Qt.Orientation.Horizontal)
        self.scale_temp.setRange(0, 20)  # 0.0 to 2.0 in tenths
        self.scale_temp.setValue(7)  # 0.7
        self.lbl_temp_val = QLabel("0.7")
        self.scale_temp.valueChanged.connect(lambda v: self.lbl_temp_val.setText(f"{v/10:.1f}"))
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.scale_temp)
        temp_layout.addWidget(self.lbl_temp_val)
        settings_layout.addRow(temp_layout)

        # Max tokens
        self.entry_max_tokens = QLineEdit("1024")
        settings_layout.addRow("最大Token:", self.entry_max_tokens)

        self.btn_randomize = QPushButton("🎲 随机设定")
        self.btn_randomize.clicked.connect(self.randomize_settings)
        settings_layout.addRow(self.btn_randomize)

        # Scenario Injection
        scenario_group = QGroupBox("场景注入 (Scenario Injection)")
        scenario_layout = QGridLayout(scenario_group)
        top_layout.addWidget(scenario_group)

        # HP
        scenario_layout.addWidget(QLabel("HP:"), 0, 0)
        self.entry_hp = QLineEdit("100")
        scenario_layout.addWidget(self.entry_hp, 0, 1)
        scenario_layout.addWidget(QLabel("/"), 0, 2)
        self.entry_max_hp = QLineEdit("100")
        scenario_layout.addWidget(self.entry_max_hp, 0, 3)

        # Money
        scenario_layout.addWidget(QLabel("金币:"), 1, 0)
        self.entry_money = QLineEdit("0")
        scenario_layout.addWidget(self.entry_money, 1, 1, 1, 2)

        # Location
        scenario_layout.addWidget(QLabel("位置:"), 2, 0)
        self.entry_location = QLineEdit("未知")
        scenario_layout.addWidget(self.entry_location, 2, 1, 1, 3)

        # Time
        scenario_layout.addWidget(QLabel("时间:"), 3, 0)
        self.entry_time = QLineEdit("清晨")
        scenario_layout.addWidget(self.entry_time, 3, 1, 1, 2)

        # Generate Button
        self.btn_generate = QPushButton("▶ 生成测试 (Generate)")
        self.btn_generate.clicked.connect(self.start_generation)
        left_layout.addWidget(self.btn_generate)

        self.status_label = QLabel("就绪")
        left_layout.addWidget(self.status_label)

        # Chat Area
        chat_group = QGroupBox("冒险记录 (Chat)")
        chat_layout = QVBoxLayout(chat_group)
        left_layout.addWidget(chat_group)

        self.chat_text = QTextEdit()
        self.chat_text.setFont(QFont("Consolas", 10))
        self.chat_text.setReadOnly(True)
        chat_layout.addWidget(self.chat_text)

        # Input Area
        input_layout = QHBoxLayout()
        left_layout.addLayout(input_layout)

        self.input_entry = QLineEdit()
        self.input_entry.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_entry)

        self.btn_send = QPushButton("发送")
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)

        # Right: Game State Components
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        main_splitter.addWidget(right_widget)

        # Raw State Block
        raw_state_group = QGroupBox("AI 原始状态输出 (<STATE_START>...<STATE_END>)")
        raw_state_layout = QVBoxLayout(raw_state_group)
        right_layout.addWidget(raw_state_group)

        self.raw_state_text = QTextEdit()
        self.raw_state_text.setFont(QFont("Consolas", 8))
        self.raw_state_text.setMaximumHeight(150)
        raw_state_layout.addWidget(self.raw_state_text)

        # Split Right Frame into Top (Notebook) and Bottom (Description)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_layout.addWidget(right_splitter)

        # Notebook Frame
        notebook_widget = QWidget()
        notebook_layout = QVBoxLayout(notebook_widget)
        right_splitter.addWidget(notebook_widget)

        # Game Components Notebook
        self.comp_notebook = QTabWidget()
        notebook_layout.addWidget(self.comp_notebook)

        # Import components directly
        from src.GUI.QtComponents.game_screen.status import StatusComponent
        from src.GUI.QtComponents.game_screen.inventory import InventoryComponent
        from src.GUI.QtComponents.game_screen.skills import SkillsComponent
        from src.GUI.QtComponents.game_screen.entities import EntitiesComponent

        # Status Tab
        self.status_component = StatusComponent(self._on_status_clicked)
        self.comp_notebook.addTab(self.status_component, "状态")

        # Inventory Tab
        self.inventory_component = InventoryComponent(
            self._on_money_clicked,
            self._on_inventory_selected,
            self._on_equipment_clicked,
            on_edit_item=self._on_edit_item,
            on_delete_item=self._on_delete_item,
            on_add_item=self._on_add_item
        )
        self.comp_notebook.addTab(self.inventory_component, "物品")

        # Skills Tab
        self.skills_component = SkillsComponent(
            self._on_skill_selected,
            on_edit=self._on_edit_skill,
            on_delete=self._on_delete_skill,
            on_add=self._on_add_skill
        )
        self.comp_notebook.addTab(self.skills_component, "技能")

        # Entities Tab
        self.entities_component = EntitiesComponent(
            self._on_entity_selected,
            on_edit=self._on_edit_entity,
            on_delete=self._on_delete_entity,
            on_add=self._on_add_entity
        )
        self.comp_notebook.addTab(self.entities_component, "实体")

        # Description Frame
        desc_group = QGroupBox("详情描述")
        desc_layout = QVBoxLayout(desc_group)
        right_splitter.addWidget(desc_group)

        self.mock_game.desc_text = QTextEdit()
        self.mock_game.desc_text.setFont(QFont("Arial", 9))
        self.mock_game.desc_text.setReadOnly(True)
        desc_layout.addWidget(self.mock_game.desc_text)

        # Set splitter proportions
        main_splitter.setSizes([400, 400])
        right_splitter.setSizes([300, 100])

    def randomize_settings(self):
        def set_random(cb, exclude_first=True):
            count = cb.count()
            if exclude_first and count > 1:
                cb.setCurrentIndex(random.randint(1, count - 1))
            elif count > 0:
                cb.setCurrentIndex(random.randint(0, count - 1))

        set_random(self.cb_birthplace)
        set_random(self.cb_race)
        set_random(self.cb_magic)

    def _construct_system_prompt(self):
        parts = self.data_manager.data.get("system_prompt_parts", {})
        system_prompt = ""
        
        for key in self.part_order:
            if key in parts:
                header = self.header_map.get(key, f"【{key}】")
                system_prompt += f"{header}\n{parts[key]}\n\n"
        
        # Add skills
        skills = self.data_manager.data.get("skills", [])
        if skills:
            skill_str = "【已知技能列表（仅供参考，可以自己生成）】\n"
            for skill in skills:
                name = skill.get('name', '未知')
                element = skill.get('element', '无')
                cost = skill.get('cost', '0')
                density = skill.get('density', '无')
                desc = skill.get('description', '无')
                skill_str += f"- {name}: [{element}] 消耗:{cost}, 浓度:{density}。效果: {desc}\n"
            system_prompt += f"\n{skill_str}\n"
            
        return system_prompt

    def start_generation(self):
        self.btn_generate.setEnabled(False)
        self.chat_text.clear()
        self.status_label.setText("正在生成...")
        
        system_prompt = self._construct_system_prompt()
        
        thread = threading.Thread(target=self.generate_opening, args=(system_prompt,))
        thread.daemon = True
        thread.start()

    def generate_opening(self, system_prompt):
        try:
            template = self.data_manager.data.get("opening_prompt_template", "")
            
            birthplace = self.cb_birthplace.currentText()
            race = self.cb_race.currentText()
            magic = self.cb_magic.currentText()
            
            if birthplace == "随机":
                options = ["北境", "南疆", "废都", "浮空城"]
                birthplace = random.choice(options)
            if race == "随机":
                options = ["人类", "高等精灵", "不死族", "魔物"]
                race = random.choice(options)
            if magic == "随机":
                options = ["低 (0-10%)", "一般 (10-20%)", "高 (70-80%)", "极高 (90-100%)"]
                magic = random.choice(options)
            
            magic_density = "15%"
            if "低" in magic: magic_density = "5%"
            elif "一般" in magic: magic_density = "15%"
            elif "高" in magic: magic_density = "75%"
            elif "极高" in magic: magic_density = "95%"

            # Get Scenario Injection Values
            hp = self.entry_hp.text()
            max_hp = self.entry_max_hp.text()
            money = self.entry_money.text()
            location = self.entry_location.text()
            time_val = self.entry_time.text()

            user_prompt = template.format(
                birthplace=birthplace,
                player_name="测试玩家",
                race=race,
                magic_density=magic_density
            )
            
            # Append Scenario Injection
            injection_text = f"\n\n【场景注入】\n请强制设定玩家初始状态如下：\n- HP: {hp}/{max_hp}\n- 金币: {money}\n- 当前位置: {location}\n- 时间: {time_val}\n请在生成的第一个状态块中反映这些数值。"
            user_prompt += injection_text
            
            self.history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Initialize Mock Player Data
            from src.Data.PlayerData import PlayerData
            self.mock_game.player_data = PlayerData(name="测试玩家")
            self.mock_game.player_data.status["race"] = race
            self.mock_game.player_data.status["magic_density"] = magic_density
            self.mock_game.player_data.status["magic"] = "100/100"
            
            # Pre-set mock data (will be overwritten by AI response usually, but good for initial display)
            try:
                self.mock_game.player_data.hp = int(hp)
                self.mock_game.player_data.max_hp = int(max_hp)
                self.mock_game.player_data.money = int(money)
                self.mock_game.world["time"] = time_val
                # Location is usually tracked in status or narrative, PlayerData doesn't have explicit location field in simple init
                self.mock_game.player_data.status["location"] = location 
            except:
                pass

            self._run_ai_chat()

        except Exception as e:
            self.chat_message_sent.emit(f"\n\n发生错误: {str(e)}", "system")
            self.ui_reset.emit()

    def send_message(self):
        msg = self.input_entry.text().strip()
        if not msg: return

        self.input_entry.clear()
        self.chat_message_sent.emit(msg, "user")
        self.history.append({"role": "user", "content": msg})

        self.status_updated.emit("AI 思考中...")
        thread = threading.Thread(target=self._run_ai_chat)
        thread.daemon = True
        thread.start()

    def _run_ai_chat(self):
        try:
            # Get parameters
            temp = self.scale_temp.value() / 10.0
            try:
                max_tokens = int(self.entry_max_tokens.text())
            except ValueError:
                max_tokens = 1024

            client = AIClient()
            full_response_buffer = []

            def on_token(token):
                full_response_buffer.append(token)
                self.chat_token_received.emit(token)

            # Only add "AI: " prefix if this is the first assistant message or after a user message
            # Check if the last message in history is from user
            if self.history and self.history[-1]["role"] == "user":
                self.chat_message_sent.emit("", "assistant_start")
            else:
                # Continue in the same assistant block
                pass
            
            full_content = client.chat(self.history, on_token=on_token, temperature=temp, max_tokens=max_tokens)
            self.history.append({"role": "assistant", "content": full_content})

            self.process_parsed_data(full_content)
            self.status_updated.emit("就绪")
        except Exception as e:
            self.chat_message_sent.emit(f"\nError: {e}", "system")
        finally:
            self.ui_reset.emit()

    def append_chat(self, text, role):
        # Use QMetaObject.invokeMethod to ensure thread safety
        QMetaObject.invokeMethod(self, "_append_chat_impl", Qt.ConnectionType.QueuedConnection,
                                Q_ARG(str, text), Q_ARG(str, role))

    def _append_chat_impl(self, text, role):
        cursor = self.chat_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        if role == "user":
            cursor.insertText(f"\n\n你: {text}")
        elif role == "system":
            cursor.insertText(f"\n{text}")
        elif role == "assistant_start":
            cursor.insertText(f"\n\nAI: {text}")
        elif role == "assistant":
            cursor.insertText(text)
        else:
            cursor.insertText(text)

        self.chat_text.ensureCursorVisible()

    def append_chat_stream(self, text):
        # Use QMetaObject.invokeMethod to ensure thread safety
        QMetaObject.invokeMethod(self, "_append_chat_stream_impl", Qt.ConnectionType.QueuedConnection,
                                Q_ARG(str, text))

    def _append_chat_stream_impl(self, text):
        cursor = self.chat_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.chat_text.ensureCursorVisible()

    def process_parsed_data(self, full_content):
        # 1. Extract Raw State
        state_match = re.search(r'<STATE_START>(.*?)<STATE_END>', full_content, re.DOTALL)
        raw_state = ""
        if state_match:
            raw_state = state_match.group(1).strip()

        self.raw_state_updated.emit(raw_state)

        # Clean state block from chat text
        chat_content = self.chat_text.toPlainText()
        while True:
            start_idx = chat_content.find("<STATE_START>")
            if start_idx == -1:
                break
            end_idx = chat_content.find("<STATE_END>", start_idx)
            if end_idx != -1:
                end_idx += len("<STATE_END>")
                chat_content = chat_content[:start_idx] + chat_content[end_idx:]
            else:
                break

        self.chat_content_updated.emit(chat_content)

        # 2. Execute Commands on Mock Game
        from src.AI.parser import AICommandExecutor

        executor = AICommandExecutor(self.mock_game)
        executor.execute_commands(raw_state)

        # 3. Update UI Components
        self.status_component.update_display(self.mock_game.status)
        self.inventory_component.update_display(
            money=self.mock_game.money,
            inventory_names=[item.get('name', str(item)) for item in self.mock_game.inventory],
            equipment_names={slot: self.mock_game.equipment.get(slot) for slot in ['head', 'body', 'legs', 'weapon', 'accessory']}
        )
        self.skills_component.set_items(self.mock_game.skills)
        self.entities_component.set_items(self.mock_game.entities)

    def reset_ui(self):
        self.btn_generate.setEnabled(True)

    # Callback methods for game components
    def _on_status_clicked(self, status_key):
        """Handle status item click"""
        pass

    def _on_money_clicked(self):
        """Handle money display click"""
        pass

    def _on_inventory_selected(self, item_name):
        """Handle inventory item selection"""
        pass

    def _on_equipment_clicked(self, slot):
        """Handle equipment slot click"""
        pass

    def _on_edit_item(self, item_name):
        """Handle item editing"""
        pass

    def _on_delete_item(self, item_name):
        """Handle item deletion"""
        pass

    def _on_add_item(self):
        """Handle adding new item"""
        pass

    def _on_skill_selected(self, skill_name):
        """Handle skill selection"""
        pass

    def _on_edit_skill(self, skill_name):
        """Handle skill editing"""
        pass

    def _on_delete_skill(self, skill_name):
        """Handle skill deletion"""
        pass

    def _on_add_skill(self):
        """Handle adding new skill"""
        pass

    def _on_entity_selected(self, entity_name):
        """Handle entity selection"""
        pass

    def _on_edit_entity(self, entity_name):
        """Handle entity editing"""
        pass

    def _on_delete_entity(self, entity_name):
        """Handle entity deletion"""
        pass

    def _on_add_entity(self):
        """Handle adding new entity"""
        pass

    def _on_chat_token_received(self, token):
        """Slot for receiving chat tokens from background thread"""
        self.append_chat_stream(token)

    def _on_chat_message_sent(self, text, role):
        """Slot for sending chat messages from background thread"""
        self.append_chat(text, role)

    def _on_status_updated(self, status):
        """Slot for updating status from background thread"""
        self.status_label.setText(status)

    def _on_ui_reset(self):
        """Slot for resetting UI from background thread"""
        self.reset_ui()

    def _on_raw_state_updated(self, raw_state):
        """Slot for updating raw state text"""
        self.raw_state_text.setPlainText(raw_state)

    def _on_chat_content_updated(self, content):
        """Slot for updating chat content"""
        self.chat_text.setPlainText(content)
