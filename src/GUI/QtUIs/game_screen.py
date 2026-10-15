import queue
from PyQt6.QtCore                      import Qt, QTimer
from PyQt6.QtWidgets                   import QVBoxLayout,QSplitter,QTabWidget
from src.Data                          import PlayerData, EntityData
from src.AI.client                     import AIClient
from src.Constants.ui_constants        import UI_TEXTS
from src.GUI.QtComponents.game_screen  import *
from src.GUI.QtComponents.SkyLayers    import *
from src.GUI.QtComponents.base.base_ui import BaseUI
from src.GUI.QtComponents.debug_utils  import debug_enabled, dump_widget_styles
from src.GUI.QtComponents.game_screen.handlers import AiFlowHandlersMixin,EntitiesHandlersMixin,InventoryHandlersMixin,PersistenceHandlersMixin,QuestsHandlersMixin,SnapshotHandlersMixin,SkillsHandlersMixin,TabBadgesHandlersMixin
class GameScreenQt(PersistenceHandlersMixin,AiFlowHandlersMixin,SnapshotHandlersMixin,TabBadgesHandlersMixin,InventoryHandlersMixin,SkillsHandlersMixin,QuestsHandlersMixin,EntitiesHandlersMixin,BaseUI,):
    def __init__(self, app_window, filename: str, save_data: dict):
        import time
        from src.utils.logger import logger
        self._debug_t0 = time.perf_counter()
        super().__init__(app_window)
        self.filename = filename
        self.save_data = save_data
        logger.info("GameScreen init start")

        # 复用共享夜空背景（层级相同则不重建）
        t_bg_start = time.perf_counter()
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)
        logger.info(f"GameScreen background setup: {time.perf_counter() - t_bg_start:.3f}s")

        self.history         : str        = save_data.get("history", [])
        self.summaries       : str        = save_data.get("summaries", [])
        self.world_name      : str        = save_data.get("world_name", save_data.get("name", "未知世界"))
        self.world           : str        = save_data.get("world", {"time": "未知", "weather": "未知"})
        self.summarized_line : int        = save_data.get("summarized_line", 0)
        
        # 如果存档中没有系统提示，自动添加最新的系统提示
        t_ensure = time.perf_counter()
        self._ensure_system_prompt()
        logger.info(f"_ensure_system_prompt: {time.perf_counter() - t_ensure:.3f}s")
        
        t_player = time.perf_counter()
        self.player_data     : PlayerData = PlayerData.from_dict(save_data)
        logger.info(f"PlayerData.from_dict: {time.perf_counter() - t_player:.3f}s")
        t_entities = time.perf_counter()
        self.entities        : list[EntityData] = []
        ent_data = save_data.get("entities", save_data.get("npcs", []))
        for n in ent_data:
            self.entities.append(EntityData.from_dict(n))
        logger.info(f"Parsed {len(self.entities)} entities in {time.perf_counter() - t_entities:.3f}s")

        # 延迟在后台初始化 AIClient，避免阻塞主线程
        self.client = None
        self.ai_client_ready = False
        def _init_aiclient_bg():
            t_bg = time.perf_counter()
            try:
                c = AIClient()
                self.client = c
                self.ai_client_ready = True
                logger.info(f"AIClient init (deferred): {time.perf_counter() - t_bg:.3f}s")
                self.summary_component._ai_client = self.client
            except Exception as e:
                logger.error(f"AIClient init failed in background: {e}", exc_info=True)
        import threading
        threading.Thread(target=_init_aiclient_bg, daemon=True).start()
        self.msg_queue = queue.Queue()
        self.is_generating = False
        self.is_first_response = (len(self.history) <= 2)

        self.hide_streaming = False
        self.stream_buffer = ""

        # 标签更新指示器（星星）
        self._tab_base_text: dict[tuple[str, int], str] = {}
        self._tab_dirty: dict[tuple[str, int], bool] = {}
        self._tab_star_phase = False
        self._tab_star_timer = QTimer(self)
        self._tab_star_timer.setInterval(320)
        self._tab_star_timer.timeout.connect(self._tick_tab_stars)

        t_ui = time.perf_counter()
        self._setup_ui()
        logger.info(f"_setup_ui: {time.perf_counter() - t_ui:.3f}s")
        # 延迟执行耗时更新，避免阻塞页面切换/淡入动画
        QTimer.singleShot(0, self.restore_history_display)
        QTimer.singleShot(10, self.update_ui_display)
        QTimer.singleShot(20, lambda: self.trigger_ai_response() if len(self.history) == 2 and self.history[-1].get("role") == "user" else None)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.process_queue)
        self._timer.start(50)
        logger.debug(f"GameScreen init scheduled deferred updates in {time.perf_counter() - self._debug_t0:.3f}s")
    
    def _ensure_system_prompt(self):
        """确保历史记录的开头有系统提示，如果没有则添加最新的系统提示"""
        from src.AI.prompts import SYSTEM_PROMPT
        from src.SaveLoad.SkillLoader import load_skills_to_string
        
        # 检查第一个消息是否为系统提示
        if not self.history or self.history[0].get("role") != "system":
            # 添加最新的系统提示
            skill_context = load_skills_to_string()
            final_system_prompt = SYSTEM_PROMPT + "\n技能示例" + skill_context
            system_msg = {"role": "system", "content": final_system_prompt}
            self.history.insert(0, system_msg)
    def _setup_ui_left_tabs(self, splitter  : QSplitter) -> QTabWidget:
        self.chat_component     = ChatComponent(self.send_player_action)
        self.entities_component = EntitiesComponent(self._on_entity_selected, debug_ctx=self)
        self.summary_component  = SummaryComponent(ai_client=self.client,msg_queue=self.msg_queue,on_save=self.save_and_quit,on_summaries_changed=self.update_ui_display,)
        left_tabs = QTabWidget()
        splitter.addWidget(left_tabs)
        left_tabs.addTab(self.chat_component, UI_TEXTS["game_screen"]["tab_adventure"])
        left_tabs.addTab(self.entities_component, UI_TEXTS["game_screen"]["tab_entities"])
        left_tabs.addTab(self.summary_component, UI_TEXTS["game_screen"]["tab_summary"])
        return left_tabs
    def _setup_ui_center_tabs(self, splitter: QSplitter) -> QTabWidget:
        center_tabs = QTabWidget()
        splitter.addWidget(center_tabs)
        self.status_component = StatusComponent(debug_ctx=self)
        self.inventory_component = InventoryComponent(None, self._on_inventory_selected, self._on_equipment_clicked, debug_ctx=self)
        self.skills_component = SkillsComponent(self._on_skill_selected, debug_ctx=self)
        self.quests_component = QuestsComponent(self._on_active_quest_selected,self._on_done_quest_selected,self._on_abandon_quest,debug_ctx=self,)
        center_tabs.addTab(self.status_component,    UI_TEXTS["game_screen"]["tab_status"])
        center_tabs.addTab(self.inventory_component, UI_TEXTS["game_screen"]["tab_inventory"])
        center_tabs.addTab(self.skills_component,    UI_TEXTS["game_screen"]["tab_skills"])
        center_tabs.addTab(self.quests_component,    UI_TEXTS["game_screen"]["tab_quests"])
        return center_tabs
    # ====== UI ======
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("GameScreenRoot")
        self.topbar = TopBarComponent(
            on_save=lambda: self.save_and_quit(True),
            on_settings=lambda: self.app_window.show_settings(return_screen_class=None),
        )
        root.addWidget(self.topbar)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)
        # 左侧标签
        self.left_tabs   = self._setup_ui_left_tabs(splitter)
        self.center_tabs = self._setup_ui_center_tabs(splitter)
        # 右侧详情
        self.detail_component = DetailComponent()
        splitter.addWidget(self.detail_component)
        splitter.setStretchFactor(2, 2)
        # 跟踪基础标签文本以用于星标徽章
        for i in range(self.left_tabs.count()):
            self._tab_base_text[("left", i)] = self.left_tabs.tabText(i)
            self._tab_dirty[("left", i)] = False
        for i in range(self.center_tabs.count()):
            self._tab_base_text[("center", i)] = self.center_tabs.tabText(i)
            self._tab_dirty[("center", i)] = False

        self.left_tabs.currentChanged.connect(lambda idx: self._clear_tab_dirty("left", idx))
        self.center_tabs.currentChanged.connect(lambda idx: self._clear_tab_dirty("center", idx))
        self._apply_theme()
        # Debug: 在 debug 模式下打印关键控件 styleSheet，帮助定位样式覆盖来源
        try:
            if debug_enabled():
                import logging
                logger = logging.getLogger(__name__)
                logger.debug("Style dump for left_tabs:\n%s", dump_widget_styles(self.left_tabs, max_depth=2))
                logger.debug("Style dump for center_tabs:\n%s", dump_widget_styles(self.center_tabs, max_depth=2))
        except Exception:
            pass
    # ====== Chat helpers ======
    def append_text(self, text: str, role: str):
        self.chat_component.append_text(text, role)
    def clear_chat(self):
        self.chat_component.clear()
    def restore_history_display(self):
        self.chat_component.restore_history_display(self.history)
    def disable_input(self):
        self.chat_component.set_enabled(False)
    def enable_input(self):
        self.chat_component.set_enabled(True)
    # ====== Data/UI refresh ======
    def update_ui_display(self):
        self.topbar.update_display(
            player_name=getattr(self.player_data, 'name', ''),
            location=getattr(self.player_data, 'location', ''),
            time_text=self.world.get('time', '未知'),
            weather=self.world.get('weather', '未知'),
        )
        # 实体
        self.entities_component.set_items(self.entities)
        # 摘要
        self.summary_component.update_display(self.summaries)
        # 状态
        status = getattr(self.player_data, 'status', {}) or {}
        self.status_component.update_display(status)
        # 库存
        inv_names = [getattr(item, 'name', str(item)) for item in getattr(self.player_data, 'inventory', []) or []]
        equip = getattr(self.player_data, 'equipment', {}) or {}
        equip_names = {slot: (getattr(val, 'name', str(val)) if val else None) for slot, val in equip.items()}
        self.inventory_component.update_display(
            money=int(getattr(self.player_data, 'money', 0) or 0),
            inventory_names=inv_names,
            equipment_names=equip_names,
        )

        # 技能
        skills_list = getattr(self.player_data, 'skills', []) or []
        self.skills_component.set_items(skills_list)

        # 任务
        quests = getattr(self.player_data, 'quests', []) or []
        active_quests = [q for q in quests if q.get("status") == "进行中"]
        done_quests = [q for q in quests if q.get("status") != "进行中"]
        self.quests_component.set_quests(active=active_quests, done=done_quests)
