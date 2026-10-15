class TabBadgesHandlersMixin:
    def _tick_tab_stars(self):
        self._tab_star_phase = not self._tab_star_phase
        self._update_tab_badges()

    def _update_tab_badges(self):
        on = self._tab_star_phase
        star_on = " ✦"
        star_off = " ✧"

        any_dirty = False
        for (group, idx), base in self._tab_base_text.items():
            dirty = self._tab_dirty.get((group, idx), False)
            if dirty:
                any_dirty = True
                text = base + (star_on if on else star_off)
            else:
                text = base

            if group == "left":
                if 0 <= idx < self.left_tabs.count():
                    if self.left_tabs.tabText(idx) != text:
                        self.left_tabs.setTabText(idx, text)
            else:
                if 0 <= idx < self.center_tabs.count():
                    if self.center_tabs.tabText(idx) != text:
                        self.center_tabs.setTabText(idx, text)

        if any_dirty:
            if not self._tab_star_timer.isActive():
                self._tab_star_timer.start()
        else:
            self._tab_star_timer.stop()

    def _clear_tab_dirty(self, group: str, idx: int):
        key = (group, idx)
        if self._tab_dirty.get(key):
            self._tab_dirty[key] = False
            self._update_tab_badges()
