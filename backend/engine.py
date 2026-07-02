import random
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from agent import OllamaAgent

class SpaceType(Enum):
    SPECIAL = "Special"
    STREET = "Street"
    RAILROAD = "Railroad"
    UTILITY = "Utility"
    TAX = "Tax"
    CHANCE = "Chance"
    CHEST = "Community Chest"

class CardAction(Enum):
    PAY_MONEY = "pay_money"
    RECEIVE_MONEY = "receive_money"
    MOVE_TO_SPACE = "move_to_space"
    MOVE_RELATIVE = "move_relative"
    PROPERTY_REPAIRS = "property_repairs"

@dataclass
class Card:
    text: str
    action: CardAction
    value: int = 0  
    house_cost: int = 0 
    hotel_cost: int = 0 

def create_chance_deck() -> List[Card]:
    return [
        Card("Advance to Go (Collect $200).", CardAction.MOVE_TO_SPACE, 0),
        Card("Advance to Boardwalk.", CardAction.MOVE_TO_SPACE, 39),
        Card("Go directly to Jail. Do not pass Go, do not collect $200.", CardAction.MOVE_TO_SPACE, 10),
        Card("Go Back 3 Spaces.", CardAction.MOVE_RELATIVE, -3),
        Card("Speeding fine $15.", CardAction.PAY_MONEY, 15),
        Card("Your building loan matures. Collect $150.", CardAction.RECEIVE_MONEY, 150),
        Card("Make general repairs on all your property. For each house pay $25. For each hotel $100.", CardAction.PROPERTY_REPAIRS, house_cost=25, hotel_cost=100)
    ]

def create_chest_deck() -> List[Card]:
    return [
        Card("Bank error in your favor. Collect $200.", CardAction.RECEIVE_MONEY, 200),
        Card("Doctor's fee. Pay $50.", CardAction.PAY_MONEY, 50),
        Card("From sale of stock you get $50.", CardAction.RECEIVE_MONEY, 50),
        Card("Holiday fund matures. Receive $100.", CardAction.RECEIVE_MONEY, 100),
        Card("Go to Jail. Go directly to jail, do not pass Go, do not collect $200.", CardAction.MOVE_TO_SPACE, 10),
        Card("You are assessed for street repairs. $40 per house. $115 per hotel.", CardAction.PROPERTY_REPAIRS, house_cost=40, hotel_cost=115)
    ]

@dataclass
class Space:
    id: int
    name: str
    space_type: SpaceType
    color: Optional[str] = None     
    price: int = 0                 
    rent: List[int] = field(default_factory=list)  
    house_cost: int = 0             
    owner_id: Optional[int] = None  
    buildings: int = 0              
    is_mortgaged: bool = False

def create_classic_board() -> List[Space]:
    return [
        Space(0, "Go", SpaceType.SPECIAL),
        Space(1, "Mediterranean Avenue", SpaceType.STREET, "Brown", 60, [2, 10, 30, 90, 160, 250], 50),
        Space(2, "Community Chest", SpaceType.CHEST),
        Space(3, "Baltic Avenue", SpaceType.STREET, "Brown", 60, [4, 20, 60, 180, 320, 450], 50),
        Space(4, "Income Tax", SpaceType.TAX, price=200),
        Space(5, "Reading Railroad", SpaceType.RAILROAD, price=200, rent=[25, 50, 100, 200]),
        Space(6, "Oriental Avenue", SpaceType.STREET, "LightBlue", 100, [6, 30, 90, 270, 400, 550], 50),
        Space(7, "Chance", SpaceType.CHANCE),
        Space(8, "Vermont Avenue", SpaceType.STREET, "LightBlue", 100, [6, 30, 90, 270, 400, 550], 50),
        Space(9, "Connecticut Avenue", SpaceType.STREET, "LightBlue", 120, [8, 40, 100, 300, 450, 600], 50),
        Space(10, "Jail / Just Visiting", SpaceType.SPECIAL),
        Space(11, "St. Charles Place", SpaceType.STREET, "Pink", 140, [10, 50, 150, 450, 625, 750], 100),
        Space(12, "Electric Company", SpaceType.UTILITY, price=150),
        Space(13, "States Avenue", SpaceType.STREET, "Pink", 140, [10, 50, 150, 450, 625, 750], 100),
        Space(14, "Virginia Avenue", SpaceType.STREET, "Pink", 160, [12, 60, 180, 500, 700, 900], 100),
        Space(15, "Pennsylvania Railroad", SpaceType.RAILROAD, price=200, rent=[25, 50, 100, 200]),
        Space(16, "St. James Place", SpaceType.STREET, "Orange", 180, [14, 70, 200, 550, 750, 950], 100),
        Space(17, "Community Chest", SpaceType.CHEST),
        Space(18, "Tennessee Avenue", SpaceType.STREET, "Orange", 180, [14, 70, 200, 550, 750, 950], 100),
        Space(19, "New York Avenue", SpaceType.STREET, "Orange", 200, [16, 80, 220, 600, 800, 1000], 100),
        Space(20, "Free Parking", SpaceType.SPECIAL),
        Space(21, "Kentucky Avenue", SpaceType.STREET, "Red", 220, [18, 90, 250, 700, 875, 1050], 150),
        Space(22, "Chance", SpaceType.CHANCE),
        Space(23, "Indiana Avenue", SpaceType.STREET, "Red", 220, [18, 90, 250, 700, 875, 1050], 150),
        Space(24, "Illinois Avenue", SpaceType.STREET, "Red", 240, [20, 100, 300, 750, 925, 1100], 150),
        Space(25, "B. & O. Railroad", SpaceType.RAILROAD, price=200, rent=[25, 50, 100, 200]),
        Space(26, "Atlantic Avenue", SpaceType.STREET, "Yellow", 260, [22, 110, 330, 800, 975, 1150], 150),
        Space(27, "Ventnor Avenue", SpaceType.STREET, "Yellow", 260, [22, 110, 330, 800, 975, 1150], 150),
        Space(28, "Water Works", SpaceType.UTILITY, price=150),
        Space(29, "Marvin Gardens", SpaceType.STREET, "Yellow", 280, [24, 120, 360, 850, 1025, 1200], 150),
        Space(30, "Go To Jail", SpaceType.SPECIAL),
        Space(31, "Pacific Avenue", SpaceType.STREET, "Green", 300, [26, 130, 390, 900, 1100, 1275], 200),
        Space(32, "North Carolina Avenue", SpaceType.STREET, "Green", 300, [26, 130, 390, 900, 1100, 1275], 200),
        Space(33, "Community Chest", SpaceType.CHEST),
        Space(34, "Pennsylvania Avenue", SpaceType.STREET, "Green", 320, [28, 150, 450, 1000, 1200, 1400], 200),
        Space(35, "Short Line", SpaceType.RAILROAD, price=200, rent=[25, 50, 100, 200]),
        Space(36, "Chance", SpaceType.CHANCE),
        Space(37, "Park Place", SpaceType.STREET, "DarkBlue", 350, [35, 175, 500, 1100, 1300, 1500], 200),
        Space(38, "Luxury Tax", SpaceType.TAX, price=100),
        Space(39, "Boardwalk", SpaceType.STREET, "DarkBlue", 400, [50, 200, 600, 1400, 1700, 2000], 200)
    ]

@dataclass
class Player:
    id: int
    name: str
    model_name: str = "llama3"
    persona: str = "Neutral AI"
    balance: int = 1500
    position: int = 0
    is_bankrupt: bool = False
    is_in_jail: bool = False
    turns_in_jail: int = 0

@dataclass
class GameState:
    turn_number: int = 1
    current_player_id: int = 0
    consecutive_doubles: int = 0 
    players: List[Player] = field(default_factory=list)
    board: List[Space] = field(default_factory=create_classic_board)
    logs: List[str] = field(default_factory=list)
    chance_deck: List[Card] = field(default_factory=create_chance_deck)
    chest_deck: List[Card] = field(default_factory=create_chest_deck)

class GameEngine:
    def __init__(self, state: GameState):
        self.state = state

    def roll_dice(self) -> Tuple[int, int]:
        return random.randint(1, 6), random.randint(1, 6)

    def execute_turn(self) -> None:
        if not self.state.players:
            return

        player = self.state.players[self.state.current_player_id]

        if player.is_bankrupt:
            self._advance_turn()
            return

        log_prefix = f"[LOG][Turn {self.state.turn_number}] {player.name}"

        # --- JAIL DECISION PHASE ---
        if player.is_in_jail:
            prompt_json = self.export_state_for_llm(player.id, player.position, "jail_decision")
            ai_agent = OllamaAgent(agent_id=player.id, name=player.name, model_name=player.model_name, persona=player.persona)
            response = ai_agent.query_llm(prompt_json)

            pub_msg = response.get("public_message")
            if pub_msg: self.state.logs.append(f"[CHAT] 💬 {player.name} says: \"{pub_msg}\"")
            
            self.state.logs.append(f"{log_prefix} [AI THOUGHT] : {response.get('chain_of_thought')}")
            
            if response.get("action") == "pay_bail" and player.balance >= 50:
                player.balance -= 50
                player.is_in_jail = False
                player.turns_in_jail = 0
                self.state.logs.append(f"{log_prefix} pays $50 bail to leave Jail. (Balance: ${player.balance})")
            else:
                self.state.logs.append(f"{log_prefix} decides to stay in Jail and roll for a double.")

        # --- MANAGEMENT PHASE ---
        self._management_phase(player)

        # 1. Dice Roll
        die1, die2 = self.roll_dice()
        total_steps = die1 + die2
        is_double = (die1 == die2)

        self.state.logs.append(f"{log_prefix} rolls the dice: {die1} + {die2} = {total_steps}." + (" (Double!)" if is_double else ""))

        # --- JAIL RESOLUTION ---
        if player.is_in_jail:
            player.turns_in_jail += 1
            if is_double:
                self.state.logs.append(f"{log_prefix} rolled a double and escapes Jail for free!")
                player.is_in_jail = False
                player.turns_in_jail = 0
                self.state.consecutive_doubles = 0 
            elif player.turns_in_jail >= 3:
                self.state.logs.append(f"{log_prefix} has been in Jail for 3 turns. Forced to pay $50.")
                player.balance -= 50
                player.is_in_jail = False
                player.turns_in_jail = 0
                if player.balance < 0:
                    self._declare_bankruptcy(player, None)
                    return
            else:
                self.state.logs.append(f"{log_prefix} did not roll a double. Remains in Jail (Turn {player.turns_in_jail}/3).")
                self._advance_turn()
                return

        # 2. Check the 3-doubles rule
        if is_double and not player.is_in_jail and player.turns_in_jail == 0:
            self.state.consecutive_doubles += 1
            if self.state.consecutive_doubles == 3:
                self.state.logs.append(f"{log_prefix} rolled 3 consecutive doubles! Sent directly to Jail.")
                player.position = 10  
                player.is_in_jail = True
                self.state.consecutive_doubles = 0
                self._advance_turn()
                return
        else:
            self.state.consecutive_doubles = 0

        # 3. Position Calculation & Go Space
        old_position = player.position
        new_position = (old_position + total_steps) % 40
        player.position = new_position

        self.state.logs.append(f"{log_prefix} moves from {self.state.board[old_position].name} ({old_position}) to {self.state.board[new_position].name} ({new_position}).")

        if new_position < old_position:
            player.balance += 200
            self.state.logs.append(f"{log_prefix} passes Go and collects $200 (New balance: ${player.balance}).")

        # 4. Evaluate Arrival Space
        self._evaluate_space(player, new_position, total_steps)

        # 5. Advance Turn or Replay on Double
        if not is_double:
            self._advance_turn()
        else:
            self.state.logs.append(f"{log_prefix} gets to roll again due to a double.")

    def _evaluate_space(self, player: Player, space_id: int, dice_roll: int) -> None:
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] {player.name}"

        if space.space_type == SpaceType.TAX:
            player.balance -= space.price
            self.state.logs.append(f"{log_prefix} pays the '{space.name}' of ${space.price} (Balance: ${player.balance}).")
            if player.balance < 0:
                self._declare_bankruptcy(player, None)
        
        elif space.space_type == SpaceType.SPECIAL and space_id == 30:
            self.state.logs.append(f"{log_prefix} goes directly to Jail.")
            player.position = 10
            player.is_in_jail = True
            self.state.consecutive_doubles = 0

        elif space.space_type in [SpaceType.CHANCE, SpaceType.CHEST]:
            self._draw_card(player, space.space_type, dice_roll)    

        elif space.space_type in [SpaceType.STREET, SpaceType.RAILROAD, SpaceType.UTILITY]:
            if space.owner_id is None:
                prompt_json = self.export_state_for_llm(player.id, space_id, "buy_property")
                ai_agent = OllamaAgent(agent_id=player.id, name=player.name, model_name=player.model_name, persona=player.persona)
                response = ai_agent.query_llm(prompt_json)
                
                pub_msg = response.get("public_message")
                if pub_msg: self.state.logs.append(f"[CHAT] 💬 {player.name} says: \"{pub_msg}\"")
                
                self.state.logs.append(f"{log_prefix} [AI THOUGHT] : {response.get('chain_of_thought', 'No thought logged.')}")
                
                if response.get('action') == "buy" and player.balance >= space.price:
                    player.balance -= space.price
                    space.owner_id = player.id
                    self.state.logs.append(f"{log_prefix} [ACTION] BUYS {space.name} for ${space.price} (Balance: ${player.balance}).")
                else:
                    self.state.logs.append(f"{log_prefix} [ACTION] REJECTS buying {space.name} for ${space.price}. Proceeding to Auction.")
                    self._execute_auction(space_id)
                    
            elif space.owner_id != player.id:
                owner = next(p for p in self.state.players if p.id == space.owner_id)
                rent = self._calculate_rent(space, dice_roll, owner)
                
                if rent > 0:
                    rent_context = {"target_name": player.name, "rent_amount": rent}
                    prompt_json = self.export_state_for_llm(owner.id, space_id, "rent_decision", rent_context=rent_context)
                    
                    owner_agent = OllamaAgent(agent_id=owner.id, name=owner.name, model_name=owner.model_name, persona=owner.persona)
                    owner_decision = owner_agent.query_llm(prompt_json)
                    
                    pub_msg = owner_decision.get("public_message")
                    if pub_msg: self.state.logs.append(f"[CHAT] 💬 {owner.name} says: \"{pub_msg}\"")
                    
                    self.state.logs.append(f"[LOG][Turn {self.state.turn_number}] {owner.name} [AI THOUGHT] : {owner_decision.get('chain_of_thought', '...')}")
                    
                    if owner_decision.get("action") == "waive_rent":
                        self.state.logs.append(f"{log_prefix} 🤝 COLLUSION : {owner.name} decides to WAIVE the ${rent} rent for {player.name} to build an alliance!")
                    else:
                        player.balance -= rent
                        owner.balance += rent
                        self.state.logs.append(f"{log_prefix} lands on {owner.name}'s property ({space.name}). Rent paid: ${rent} (Balance: ${player.balance}).")
                        
                        if player.balance < 0:
                            self._declare_bankruptcy(player, owner)

    def _advance_turn(self) -> None:
        num_players = len(self.state.players)
        if num_players == 0:
            return
            
        next_id = (self.state.current_player_id + 1) % num_players
        
        loop_guard = 0
        while self.state.players[next_id].is_bankrupt and loop_guard < num_players:
            next_id = (next_id + 1) % num_players
            loop_guard += 1
            
        self.state.current_player_id = next_id
        self.state.turn_number += 1

    def export_state_for_llm(self, player_id: int, space_id: int, action_type: str, locked_spaces: set = None, trade_offer: dict = None, rent_context: dict = None) -> str:
        if locked_spaces is None:
            locked_spaces = set()
            
        player = next(p for p in self.state.players if p.id == player_id)
        current_space = self.state.board[space_id]
        
        legal_actions = {}
        if action_type == "buy_property":
            legal_actions = {"allowed_actions": ["buy", "pass"]} if player.balance >= current_space.price else {"allowed_actions": ["pass"]}
        elif action_type == "auction_bid":
            legal_actions = {
                "allowed_actions": ["bid", "pass"], 
                "max_bid_possible_due_to_liquidity": player.balance,
                "property_base_price": current_space.price,
                "WARNING": f"Do not bid your entire balance! Bidding significantly more than the base_price (${current_space.price}) is mathematically ruinous."
            }
        elif action_type == "jail_decision":
            legal_actions = {"allowed_actions": ["pay_bail", "wait"]} if player.balance >= 50 else {"allowed_actions": ["wait"]}
        elif action_type == "evaluate_trade":
            legal_actions = {"allowed_actions": ["accept_trade", "reject_trade"]}
        elif action_type == "rent_decision":
            legal_actions = {"allowed_actions": ["charge_rent", "waive_rent"]}
        elif action_type == "management":
            tradeable_owned = [s.id for s in self.state.board if s.owner_id == player.id and not any(other.buildings > 0 for other in self.state.board if other.color == s.color)]
            tradeable_others = [s.id for s in self.state.board if s.owner_id is not None and s.owner_id != player.id and not any(other.buildings > 0 for other in self.state.board if other.color == s.color)]
            
            legal_actions = {
                "allowed_actions": ["pass", "build", "mortgage", "unmortgage", "propose_trade"],
                "valid_targets_for_build": [s.id for s in self.state.board if s.owner_id == player.id and s.space_type == SpaceType.STREET and self._has_monopoly(s.color, player.id) and s.buildings < 5 and player.balance >= s.house_cost and s.id not in locked_spaces],
                "valid_targets_for_mortgage": [s.id for s in self.state.board if s.owner_id == player.id and not s.is_mortgaged and s.buildings == 0 and s.id not in locked_spaces],
                "valid_targets_for_unmortgage": [s.id for s in self.state.board if s.owner_id == player.id and s.is_mortgaged and player.balance >= int((s.price // 2) * 1.1) and s.id not in locked_spaces],
                "valid_opponents_for_trade": [p.id for p in self.state.players if p.id != player.id and not p.is_bankrupt],
                "your_tradeable_properties": tradeable_owned,
                "opponents_tradeable_properties": tradeable_others
            }

        market_status = [
            {
                "id": s.id, 
                "name": s.name, 
                "color": s.color,
                "price": s.price, 
                "house_cost": s.house_cost,
                "buildings": s.buildings,
                "owner_id": s.owner_id,
                "is_mortgaged": s.is_mortgaged,
                "mortgage_value": s.price // 2,
                "unmortgage_cost": int((s.price // 2) * 1.1)
            } 
            for s in self.state.board if s.price > 0
        ]
        
        opponents = [
            {
                "id": p.id,
                "name": p.name,
                "balance": p.balance,
                "position": p.position,
                "is_in_jail": p.is_in_jail
            }
            for p in self.state.players if p.id != player_id and not p.is_bankrupt
        ]

        llm_context = {
            "game_turn": self.state.turn_number,
            "action_required": action_type,
            "legal_actions": legal_actions,
            "trade_offer_to_evaluate": trade_offer,
            "rent_context": rent_context,
            "your_agent": {
                "id": player.id,
                "name": player.name,
                "balance": player.balance,
                "position": player.position
            },
            "opponents_overview": opponents,
            "space_details": {
                "id": current_space.id,
                "name": current_space.name,
                "base_price": current_space.price,
                "type": current_space.space_type.value,
                "owner": current_space.owner_id
            },
            "market_overview": market_status
        }
        
        return json.dumps(llm_context, indent=2, ensure_ascii=False)
    
    def _has_monopoly(self, color: str, owner_id: int) -> bool:
        color_group = [s for s in self.state.board if s.color == color]
        return all(s.owner_id == owner_id for s in color_group)

    def _calculate_rent(self, space: Space, dice_roll: int, owner: Player) -> int:
        if space.is_mortgaged:
            return 0 
            
        if space.space_type == SpaceType.STREET:
            if space.buildings == 0 and space.color and self._has_monopoly(space.color, owner.id):
                return space.rent[0] * 2
            return space.rent[space.buildings]
            
        elif space.space_type == SpaceType.RAILROAD:
            railroads_owned = sum(1 for s in self.state.board if s.space_type == SpaceType.RAILROAD and s.owner_id == owner.id and not s.is_mortgaged)
            return space.rent[railroads_owned - 1] if railroads_owned > 0 else 0
            
        elif space.space_type == SpaceType.UTILITY:
            utilities_owned = sum(1 for s in self.state.board if s.space_type == SpaceType.UTILITY and s.owner_id == owner.id and not s.is_mortgaged)
            multiplier = 10 if utilities_owned == 2 else 4
            return dice_roll * multiplier
            
        return 0
    
    def _draw_card(self, player: Player, deck_type: SpaceType, dice_roll: int) -> None:
        deck_name = "Chance" if deck_type == SpaceType.CHANCE else "Community Chest"
        deck = self.state.chance_deck if deck_type == SpaceType.CHANCE else self.state.chest_deck
        
        card = random.choice(deck)
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🃏 CARD ({deck_name})"
        self.state.logs.append(f"{log_prefix} : {player.name} draws -> '{card.text}'")

        if card.action == CardAction.PAY_MONEY:
            player.balance -= card.value
            self.state.logs.append(f"{log_prefix} : {player.name} pays ${card.value}. (Balance: ${player.balance})")
            if player.balance < 0:
                self._declare_bankruptcy(player, None)

        elif card.action == CardAction.RECEIVE_MONEY:
            player.balance += card.value
            self.state.logs.append(f"{log_prefix} : {player.name} receives ${card.value}. (Balance: ${player.balance})")

        elif card.action == CardAction.MOVE_TO_SPACE:
            old_position = player.position
            player.position = card.value
            
            if card.value == 10:
                player.is_in_jail = True
                self.state.consecutive_doubles = 0
                self.state.logs.append(f"{log_prefix} : {player.name} goes directly to Jail.")
            elif card.value < old_position and old_position != 36: 
                 player.balance += 200
                 self.state.logs.append(f"{log_prefix} : {player.name} passes Go and collects $200.")
                 
            if card.value != 10:
                self._evaluate_space(player, player.position, dice_roll)

        elif card.action == CardAction.MOVE_RELATIVE:
            new_position = (player.position + card.value) % 40
            player.position = new_position
            self.state.logs.append(f"{log_prefix} : {player.name} moves to Space {new_position}.")
            self._evaluate_space(player, new_position, dice_roll)

        elif card.action == CardAction.PROPERTY_REPAIRS:
            houses = sum(s.buildings for s in self.state.board if s.owner_id == player.id and s.buildings < 5)
            hotels = sum(1 for s in self.state.board if s.owner_id == player.id and s.buildings == 5)
            
            total_cost = (houses * card.house_cost) + (hotels * card.hotel_cost)
            if total_cost > 0:
                player.balance -= total_cost
                self.state.logs.append(f"{log_prefix} : {player.name} pays ${total_cost} for repairs ({houses} houses, {hotels} hotels). (Balance: ${player.balance})")
                if player.balance < 0:
                    self._declare_bankruptcy(player, None)
            else:
                self.state.logs.append(f"{log_prefix} : {player.name} owns no buildings. Pays $0.")
    
    def _process_build(self, player: Player, space_id: int) -> bool:
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🏗️ CONSTRUCTION"

        if space.space_type != SpaceType.STREET or space.owner_id != player.id:
            self.state.logs.append(f"{log_prefix} : {player.name} cannot build on {space.name} (Invalid target).")
            return False

        if not self._has_monopoly(space.color, player.id):
            self.state.logs.append(f"{log_prefix} : {player.name} needs the full {space.color} monopoly to build on {space.name}.")
            return False

        if space.buildings >= 5:
            self.state.logs.append(f"{log_prefix} : {space.name} already has a Hotel (max capacity).")
            return False

        if player.balance < space.house_cost:
            self.state.logs.append(f"{log_prefix} : {player.name} lacks funds to build on {space.name} (${space.house_cost} needed).")
            return False

        color_group = [s for s in self.state.board if s.color == space.color]
        min_buildings_in_group = min(s.buildings for s in color_group)
        if space.buildings > min_buildings_in_group:
            self.state.logs.append(f"{log_prefix} : {player.name} must build evenly. Cannot add house to {space.name} yet.")
            return False

        player.balance -= space.house_cost
        space.buildings += 1
        building_type = "a House" if space.buildings < 5 else "a Hotel"
        self.state.logs.append(f"{log_prefix} : {player.name} successfully built {building_type} on {space.name} for ${space.house_cost}. (Balance: ${player.balance})")
        return True

    def _declare_bankruptcy(self, bankrupt_player: Player, creditor: Optional[Player]) -> None:
        bankrupt_player.is_bankrupt = True
        
        for space in self.state.board:
            if space.owner_id == bankrupt_player.id:
                if creditor is not None:
                    space.owner_id = creditor.id 
                else:
                    space.owner_id = None 
                    space.buildings = 0  

        log_prefix = f"[LOG][Turn {self.state.turn_number}] 💀 BANKRUPTCY"
        if creditor:
            self.state.logs.append(f"{log_prefix} : {bankrupt_player.name} is ruined by {creditor.name} and surrenders all properties!")
        else:
            self.state.logs.append(f"{log_prefix} : {bankrupt_player.name} is ruined by the Bank. Properties return to the market.")
        
        from agent import OllamaAgent
        dying_agent = OllamaAgent(agent_id=bankrupt_player.id, name=bankrupt_player.name, model_name=bankrupt_player.model_name, persona=bankrupt_player.persona)
        
        context_logs = self.state.logs[-15:] 
        dying_agent.trigger_post_mortem(context_logs)

    def _management_phase(self, active_player: Player) -> None:
        log_prefix_action = f"[LOG][Turn {self.state.turn_number}] 🧠 MANAGEMENT PHASE ({active_player.name})"
        log_prefix_thought = f"[LOG][Turn {self.state.turn_number}] {active_player.name}"
        
        actions_taken = 0
        max_actions = 10 
        locked_spaces = set() 
        traded_opponents = set()
        
        while actions_taken < max_actions:
            prompt_json = self.export_state_for_llm(active_player.id, active_player.position, "management", locked_spaces)
            ai_agent = OllamaAgent(agent_id=active_player.id, name=active_player.name, model_name=active_player.model_name, persona=active_player.persona)
            agent_decision = ai_agent.query_llm(prompt_json)
            
            pub_msg = agent_decision.get("public_message")
            if pub_msg: self.state.logs.append(f"[CHAT] 💬 {active_player.name} says: \"{pub_msg}\"")
            
            thought = agent_decision.get("chain_of_thought", "No thought logged.")
            self.state.logs.append(f"{log_prefix_thought} [AI THOUGHT] : {thought}")
            
            action = agent_decision.get("action", "pass")
            
            if action == "pass":
                break 
                
            elif action == "propose_trade":
                target_id = agent_decision.get("target_agent_id")
                if target_id is None or target_id in traded_opponents:
                    self.state.logs.append(f"{log_prefix_action} : Invalid trade target or already traded this turn. Forced to pass.")
                    break
                
                success = self._process_trade_proposal(active_player, target_id, agent_decision)
                traded_opponents.add(target_id)
                actions_taken += 1
                if not success:
                    break

            elif action in ["build", "mortgage", "unmortgage"]:
                target_space_id = agent_decision.get("target_space_id")
                
                if target_space_id is None or not isinstance(target_space_id, int) or target_space_id < 0 or target_space_id > 39:
                    self.state.logs.append(f"{log_prefix_action} : Hallucination prevented (invalid ID '{target_space_id}'). Forced to pass.")
                    break
                
                if target_space_id in locked_spaces:
                    self.state.logs.append(f"{log_prefix_action} : AI tried to interact with space {target_space_id} multiple times. Forced to pass.")
                    break
                    
                if action == "build":
                    success = self._process_build(active_player, target_space_id)
                elif action == "mortgage":
                    success = self._process_mortgage(active_player, target_space_id)
                else:
                    success = self._process_unmortgage(active_player, target_space_id)
                    
                if not success:
                    break 
                
                locked_spaces.add(target_space_id)
                actions_taken += 1
            else:
                self.state.logs.append(f"{log_prefix_action} : AI returned invalid action '{action}'. Ending phase.")
                break
                
        if actions_taken >= max_actions:
            self.state.logs.append(f"{log_prefix_action} : AI reached the maximum of {max_actions} management actions. Moving to dice roll.")

    def _process_trade_proposal(self, proposer: Player, target_id: int, decision: dict) -> bool:
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🤝 TRADE"
        target_player = next((p for p in self.state.players if p.id == target_id and not p.is_bankrupt), None)
        
        if not target_player:
            return False
            
        offer_cash = int(decision.get("offer_cash", 0))
        offer_props = decision.get("offer_properties", [])
        req_props = decision.get("request_properties", [])
        
        # --- ANTI-HALLUCINATION SHIELD (Types & Boundaries) ---
        if not isinstance(offer_props, list) or not isinstance(req_props, list):
            self.state.logs.append(f"{log_prefix} : {proposer.name} hallucinated the trade format. Trade cancelled.")
            return False
            
        try:
            # Force conversion to integers
            offer_props = [int(p) for p in offer_props]
            req_props = [int(p) for p in req_props]
        except (ValueError, TypeError):
            self.state.logs.append(f"{log_prefix} : {proposer.name} hallucinated property IDs (used text instead of numbers). Trade cancelled.")
            return False
        # ------------------------------------------------------
        
        if offer_cash > proposer.balance or offer_cash < 0:
            self.state.logs.append(f"{log_prefix} : {proposer.name} offered illegal cash amount. Trade cancelled.")
            return False
            
        for pid in offer_props:
            if pid < 0 or pid > 39 or self.state.board[pid].owner_id != proposer.id: return False
        for pid in req_props:
            if pid < 0 or pid > 39 or self.state.board[pid].owner_id != target_player.id: return False

        trade_details = {
            "proposer_name": proposer.name,
            "offered_cash": offer_cash,
            "offered_properties": [self.state.board[p].name for p in offer_props],
            "requested_properties": [self.state.board[p].name for p in req_props]
        }
        
        self.state.logs.append(f"{log_prefix} : {proposer.name} PROPOSES a trade to {target_player.name} -> Offers ${offer_cash} + {trade_details['offered_properties']} for {trade_details['requested_properties']}")

        prompt_json = self.export_state_for_llm(target_player.id, target_player.position, "evaluate_trade", trade_offer=trade_details)
        from agent import OllamaAgent
        target_agent = OllamaAgent(agent_id=target_player.id, name=target_player.name, model_name=target_player.model_name, persona=target_player.persona)
        target_decision = target_agent.query_llm(prompt_json)
        
        pub_msg = target_decision.get("public_message")
        if pub_msg: self.state.logs.append(f"[CHAT] 💬 {target_player.name} says: \"{pub_msg}\"")
        
        self.state.logs.append(f"[LOG][Turn {self.state.turn_number}] {target_player.name} [AI THOUGHT] : {target_decision.get('chain_of_thought', '...')}")
        
        if target_decision.get("action") == "accept_trade":
            proposer.balance -= offer_cash
            target_player.balance += offer_cash
            for pid in offer_props: self.state.board[pid].owner_id = target_player.id
            for pid in req_props: self.state.board[pid].owner_id = proposer.id
            self.state.logs.append(f"{log_prefix} : ✅ {target_player.name} ACCEPTS the trade!")
            return True
        else:
            self.state.logs.append(f"{log_prefix} : ❌ {target_player.name} REJECTS the trade.")
            return False

    def _process_mortgage(self, player: Player, space_id: int) -> bool:
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🏦 BANK"
        
        if space.owner_id != player.id or space.is_mortgaged:
            return False
            
        if space.buildings > 0:
            self.state.logs.append(f"{log_prefix} : {player.name} cannot mortgage {space.name} while it has buildings. Sell them first.")
            return False
            
        mortgage_value = space.price // 2
        space.is_mortgaged = True
        player.balance += mortgage_value
        self.state.logs.append(f"{log_prefix} : {player.name} mortgages {space.name} and receives ${mortgage_value}. (Balance: ${player.balance})")
        return True

    def _process_unmortgage(self, player: Player, space_id: int) -> bool:
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🏦 BANK"
        
        if space.owner_id != player.id or not space.is_mortgaged:
            return False
            
        unmortgage_cost = int((space.price // 2) * 1.1)
        if player.balance < unmortgage_cost:
            self.state.logs.append(f"{log_prefix} : {player.name} cannot afford to unmortgage {space.name} (Requires ${unmortgage_cost}).")
            return False
            
        space.is_mortgaged = False
        player.balance -= unmortgage_cost
        self.state.logs.append(f"{log_prefix} : {player.name} unmortgages {space.name} for ${unmortgage_cost}. (Balance: ${player.balance})")
        return True    

    def _execute_auction(self, space_id: int) -> None:
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🔨 AUCTION"
        self.state.logs.append(f"{log_prefix} : {space.name} is up for auction!")

        active_players = [p for p in self.state.players if not p.is_bankrupt]
        bids = {}
        pending_logs = []

        for p in active_players:
            prompt_json = self.export_state_for_llm(p.id, space_id, "auction_bid")
            ai_agent = OllamaAgent(agent_id=p.id, name=p.name, model_name=p.model_name, persona=p.persona)
            response = ai_agent.query_llm(prompt_json)

            pub_msg = response.get("public_message")
            if pub_msg: pending_logs.append(f"[CHAT] 💬 {p.name} says: \"{pub_msg}\"")

            thought = response.get("chain_of_thought", "No thought logged.")
            log_prefix_agent = f"[LOG][Turn {self.state.turn_number}] {p.name}"
            pending_logs.append(f"{log_prefix_agent} [AI THOUGHT] : {thought}")

            bid_amount = response.get("bid")
            if bid_amount is None or not isinstance(bid_amount, (int, float)):
                bid_amount = 0
            else:
                try:
                    bid_amount = int(bid_amount)
                except ValueError:
                    bid_amount = 0
            
            bid_amount = min(bid_amount, p.balance)

            if bid_amount > 0:
                bids[p.id] = bid_amount
                pending_logs.append(f"{log_prefix} : {p.name} bids ${bid_amount} for the property.")
            else:
                pending_logs.append(f"{log_prefix} : {p.name} passes on the auction.")

        self.state.logs.extend(pending_logs)

        if bids:
            highest_bidder_id = max(bids, key=bids.get)
            winning_bid = bids[highest_bidder_id]
            winner = next(p for p in self.state.players if p.id == highest_bidder_id)

            winner.balance -= winning_bid
            space.owner_id = winner.id
            self.state.logs.append(f"{log_prefix} : 🏆 {winner.name} WINS the auction for {space.name} at ${winning_bid}! (Balance: ${winner.balance})")
        else:
            self.state.logs.append(f"{log_prefix} : No one bid. {space.name} remains unsold.")