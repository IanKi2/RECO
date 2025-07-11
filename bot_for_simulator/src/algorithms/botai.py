class BotAI:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.internal_state = {}
        self.vision_radius = self.config.get("vision_radius", 5)
        # Инициализация атрибутов для размеров мира
        self.world_width = None
        self.world_height = None

    def step(self, state: dict) -> tuple:
        try:
            # Сохраняем размеры мира при первом получении
            if self.world_width is None:
                self.world_width = state.get('width')
                self.world_height = state.get('height')
                print(f"World size detected: {self.world_width}x{self.world_height}")
            
            self._update_internal_state(state)
            decision = self._make_decision()
            path = self._calculate_path()
            
            command_body = self._format_command(decision)
            viz_data = {"path": path}
            
            return command_body, viz_data
            
        except Exception as e:
            print(f"Algorithm error: {str(e)}")
            return {"command": "attack"}, None

    def _update_internal_state(self, state: dict):
        self.internal_state["agent_pos"] = (state["agent"]["x"], state["agent"]["y"])
        # Сохраняем другие важные данные
        self.internal_state["npcs"] = state.get("npcs", [])
        self.internal_state["resources"] = state.get("resources", [])
        self.internal_state["obstacles"] = state.get("obstacles", [])

    def _make_decision(self) -> str:

        return "left"

    def _calculate_path(self) -> list:
        """Пример пути для визуализации"""
        agent_x, agent_y = self.internal_state["agent_pos"]
        return [
            (agent_x, agent_y),
            (agent_x + 1, agent_y),
            (agent_x + 1, agent_y + 1)
        ]
    
    def _format_command(self, decision: str) -> dict:
        return {
            "command": "move",
            "direction": decision
        }