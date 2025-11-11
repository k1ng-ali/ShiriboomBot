from dataclasses import dataclass, field
from typing import Dict, List, Any

ITEMS = ["✊", "✌", "✋"]

@dataclass
class Game:
    inviter_id: str
    inviter_name: str
    message_id: str
    opponent_id: str | None = None
    inviter_choice: str | None = None
    opponent_choice: str | None = None
    opponent_name: str | None = None
    winner: str | None = None

@dataclass
class GameManager:
    Games: Dict[str, Game] = field(default_factory=dict)

    def is_running(self, inviter_id:str) -> bool:
        return inviter_id in self.Games

    def create_game(self, inviter_id: str, inviter_name: str,inviter_choice: str, message_id:str) -> bool:
        if inviter_id not in self.Games:
            new_game = Game(inviter_id=inviter_id,
                            inviter_choice=inviter_choice,
                            inviter_name=inviter_name,
                            message_id=message_id)
            self.Games[inviter_id] = new_game
            return True
        else:
            return False

    def get_game(self, inviter_id) -> Game | None:
        return self.Games.get(inviter_id)

    def del_game(self, inviter_id:str):
        if inviter_id in self.Games:
            self.Games.pop(inviter_id, None)

    def check_result(self, inviter_id:str, opponent_id: str,
                     opponent_choice: str, opponent_name:str) -> Game | None:
        if inviter_id in self.Games:
            game = self.Games[inviter_id]
            game.opponent_id = opponent_id
            game.opponent_choice = opponent_choice
            game.opponent_name = opponent_name
            if game.inviter_choice == game.opponent_choice:
                game.winner = "draw"
                return game
            inviter_idx = ITEMS.index(game.inviter_choice)
            opponent_idx = ITEMS.index(game.opponent_choice)

            if (inviter_idx + 1) % 3 == opponent_idx:
                game.winner = "inviter"
                return game
            else:
                game.winner = "opponent"
                return game
        else:
            return None

