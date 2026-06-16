import random
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from agent import MockAgent

class SpaceType(Enum):
    SPECIAL = "Special"             # Go, Jail, Free Parking, Go to Jail
    STREET = "Street"               # Standard streets
    RAILROAD = "Railroad"           # 4 Railroads
    UTILITY = "Utility"             # Water Works and Electric Company
    TAX = "Tax"                     # Income and Luxury Tax
    CHANCE = "Chance"               # Chance cards
    CHEST = "Community Chest"       # Community Chest

class CardAction(Enum):
    PAY_MONEY = "pay_money"
    RECEIVE_MONEY = "receive_money"
    MOVE_TO_SPACE = "move_to_space"
    MOVE_RELATIVE = "move_relative"
    PROPERTY_REPAIRS = "property_repairs" # The ultimate AI trap!

@dataclass
class Card:
    text: str
    action: CardAction
    value: int = 0  # Amount of money, or space ID, or relative movement
    house_cost: int = 0 # For repairs
    hotel_cost: int = 0 # For repairs

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
    buildings: int = 0              # 0-4 houses, 5 = Hotel
    is_mortgaged: bool = False

def create_classic_board() -> List[Space]:
    """Generates the official 40 spaces of the US Classic Monopoly board."""
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
    balance: int = 1500
    position: int = 0
    is_bankrupt: bool = False
    is_in_jail: bool = False
    turns_in_jail: int = 0

@dataclass
class TradeOffer:
    sender_id: int
    target_id: int
    properties_offered: List[int] = field(default_factory=list)
    cash_offered: int = 0
    properties_requested: List[int] = field(default_factory=list)
    cash_requested: int = 0
    justification: str = "" 

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
        """Generates a deterministic 2-dice roll for the simulation."""
        return random.randint(1, 6), random.randint(1, 6)

    def execute_turn(self) -> None:
        """Executes the complete routine of a player's turn."""
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
            ai_agent = MockAgent(agent_id=player.id, name=player.name)
            response = ai_agent.query_llm(prompt_json)

            self.state.logs.append(f"{log_prefix} [AI THOUGHT] : {response.get('chain_of_thought')}")
            
            if response.get("action") == "pay_bail" and player.balance >= 50:
                player.balance -= 50
                player.is_in_jail = False
                player.turns_in_jail = 0
                self.state.logs.append(f"{log_prefix} pays $50 bail to leave Jail. (Balance: ${player.balance})")
            else:
                self.state.logs.append(f"{log_prefix} decides to stay in Jail and roll for a double.")

        # --- MANAGEMENT PHASE ---
        # Note: In official rules, you can still trade/build while in jail!
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
                self.state.consecutive_doubles = 0 # Double used to escape does not grant a replay
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

        # 2. Check the 3-doubles rule (Only if not escaping jail this turn)
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
        """Applies the economic rules of the landed space."""
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] {player.name}"

        # 1. Tax and Jail Handling
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

        # 2. Property Handling (Purchase or Rent)
        elif space.space_type in [SpaceType.STREET, SpaceType.RAILROAD, SpaceType.UTILITY]:
            if space.owner_id is None:
                # --- AI DECISION FLOW ---
                # A. Tell the AI we are specifically trying to buy a property
                prompt_json = self.export_state_for_llm(player.id, space_id, "buy_property")
                
                ai_agent = MockAgent(agent_id=player.id, name=player.name, persona="balanced")
                response = ai_agent.query_llm(prompt_json)
                
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
                
                player.balance -= rent
                owner.balance += rent
                self.state.logs.append(f"{log_prefix} lands on {owner.name}'s property ({space.name}). Rent paid: ${rent} (Balance: ${player.balance}).")
                
                if player.balance < 0:
                    self._declare_bankruptcy(player, owner)

    def _advance_turn(self) -> None:
        """Cycles to the next active player and increments the game clock."""
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

    def export_state_for_llm(self) -> str:
        # Note: Added the proper signature based on the usage in code
        pass

    def export_state_for_llm(self, player_id: int, space_id: int, action_type: str) -> str:
        """Exports the raw game state. Zero strategic help, just facts."""
        player = next(p for p in self.state.players if p.id == player_id)
        current_space = self.state.board[space_id]
        
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

        llm_context = {
            "game_turn": self.state.turn_number,
            "action_required": action_type, # <-- Now dynamic
            "your_agent": {
                "id": player.id,
                "name": player.name,
                "balance": player.balance,
                "position": player.position
            },
            "space_details": {
                "id": current_space.id,
                "name": current_space.name,
                "base_price": current_space.price,
                "type": current_space.space_type.value
            },
            "market_overview": market_status,
            "recent_logs": self.state.logs[-5:]
        }
        
        return json.dumps(llm_context, indent=2, ensure_ascii=False)
    
    def _has_monopoly(self, color: str, owner_id: int) -> bool:
        """Checks if a player owns all streets of a specific color."""
        color_group = [s for s in self.state.board if s.color == color]
        return all(s.owner_id == owner_id for s in color_group)

    def _calculate_rent(self, space: Space, dice_roll: int, owner: Player) -> int:
        """Calculates exact rent based on property type, monopolies, and buildings."""
        if space.is_mortgaged:
            return 0 # NOUVEAU: Aucun loyer si hypothéqué
            
        if space.space_type == SpaceType.STREET:
            # If no buildings but player has monopoly, rent is doubled
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
        """Draws a card and applies its effects."""
        deck_name = "Chance" if deck_type == SpaceType.CHANCE else "Community Chest"
        deck = self.state.chance_deck if deck_type == SpaceType.CHANCE else self.state.chest_deck
        
        # Draw a random card
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
            
            # Going to Jail logic
            if card.value == 10:
                player.is_in_jail = True
                self.state.consecutive_doubles = 0
                self.state.logs.append(f"{log_prefix} : {player.name} goes directly to Jail.")
            # Passing Go logic (only if moving forward and not going to jail)
            elif card.value < old_position and old_position != 36: # Exclude Chance 36 to Go
                 player.balance += 200
                 self.state.logs.append(f"{log_prefix} : {player.name} passes Go and collects $200.")
                 
            # Re-evaluate the new space!
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
        """
        Attempts to build a house/hotel on a given space. 
        Enforces Monopoly rules (monopoly ownership, even building, funds).
        Returns True if successful, False otherwise.
        """
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

        # Even Build Rule: Cannot build if another property in the color group has fewer buildings
        color_group = [s for s in self.state.board if s.color == space.color]
        min_buildings_in_group = min(s.buildings for s in color_group)
        if space.buildings > min_buildings_in_group:
            self.state.logs.append(f"{log_prefix} : {player.name} must build evenly. Cannot add house to {space.name} yet.")
            return False

        # Execute construction
        player.balance -= space.house_cost
        space.buildings += 1
        building_type = "a House" if space.buildings < 5 else "a Hotel"
        self.state.logs.append(f"{log_prefix} : {player.name} successfully built {building_type} on {space.name} for ${space.house_cost}. (Balance: ${player.balance})")
        return True

    def _declare_bankruptcy(self, bankrupt_player: Player, creditor: Optional[Player]) -> None:
        """Handles player elimination and asset transfer."""
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
        
        # --- TRIGGER POST-MORTEM ---
        from agent import MockAgent
        dying_agent = MockAgent(agent_id=bankrupt_player.id, name=bankrupt_player.name)
        
        context_logs = self.state.logs[-15:] 
        dying_agent.trigger_post_mortem(context_logs)

    def _management_phase(self, active_player: Player) -> None:
        """Allows the agent to execute transactions before rolling the dice."""
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🧠 MANAGEMENT PHASE ({active_player.name})"
        
        while True:
            # Tell the AI it is in the management phase, not buying
            prompt_json = self.export_state_for_llm(active_player.id, active_player.position, "management")
            ai_agent = MockAgent(agent_id=active_player.id, name=active_player.name)
            agent_decision = ai_agent.query_llm(prompt_json)
            
            action = agent_decision.get("action", "pass")
            
            if action == "pass":
                break 
                
            elif action == "build":
                target_space_id = agent_decision.get("target_space_id")
                self.state.logs.append(f"{log_prefix} : [AI THOUGHT] {agent_decision.get('chain_of_thought')}")
                success = self._process_build(active_player, target_space_id)
                if not success:
                    break # Break if build fails to avoid infinite loop

            elif action == "trade":
                trade_details = agent_decision["trade_details"]
                target_id = trade_details["target_agent_id"]
                self._process_trade(active_player, target_id, trade_details)
                break 

            elif action == "mortgage":
                target_space_id = agent_decision.get("target_space_id")
                self.state.logs.append(f"{log_prefix} : [AI THOUGHT] {agent_decision.get('chain_of_thought')}")
                success = self._process_mortgage(active_player, target_space_id)
                if not success:
                    break

            elif action == "unmortgage":
                target_space_id = agent_decision.get("target_space_id")
                self.state.logs.append(f"{log_prefix} : [AI THOUGHT] {agent_decision.get('chain_of_thought')}")
                success = self._process_unmortgage(active_player, target_space_id)
                if not success:
                    break
            
            else:
                # FAILSAFE: If the AI hallucinates an unknown action, force it to pass
                self.state.logs.append(f"{log_prefix} : AI returned invalid action '{action}'. Ending phase.")
                break

    def _process_trade(self, sender: Player, target_id: int, trade_details: dict) -> None:
        """Queries the target agent and executes the transfer if accepted."""
        target_player = next(p for p in self.state.players if p.id == target_id)
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🤝 NEGOTIATION"
        
        offered_cash = trade_details["offer"]["cash"]
        requested_cash = trade_details["request"]["cash"]
        self.state.logs.append(f"{log_prefix} : {sender.name} proposes a trade to {target_player.name} (+${offered_cash} against -${requested_cash} and properties).")

        # --- TARGET AGENT RESPONSE ---
        target_accepts = False 
        
        if target_accepts:
            self.state.logs.append(f"{log_prefix} : {target_player.name} ACCEPTS the offer!")
            
            sender.balance = sender.balance - offered_cash + requested_cash
            target_player.balance = target_player.balance + offered_cash - requested_cash
            
            for prop_id in trade_details["offer"]["property_ids"]:
                self.state.board[prop_id].owner_id = target_player.id
            for prop_id in trade_details["request"]["property_ids"]:
                self.state.board[prop_id].owner_id = sender.id
                
        else:
            self.state.logs.append(f"{log_prefix} : {target_player.name} REJECTS the offer.")

    def _process_mortgage(self, player: Player, space_id: int) -> bool:
        """Executes a mortgage on a property (grants 50% of base price in cash)."""
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
        """Lifts a mortgage by paying the value + 10% interest."""
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
        """Executes a single-round sealed-bid auction for an unowned property."""
        space = self.state.board[space_id]
        log_prefix = f"[LOG][Turn {self.state.turn_number}] 🔨 AUCTION"
        self.state.logs.append(f"{log_prefix} : {space.name} is up for auction!")

        active_players = [p for p in self.state.players if not p.is_bankrupt]
        bids = {}

        # 1. Collect sealed bids from all active players
        for p in active_players:
            # Tell the AI it is in an auction context
            prompt_json = self.export_state_for_llm(p.id, space_id, "auction_bid")
            ai_agent = MockAgent(agent_id=p.id, name=p.name)
            response = ai_agent.query_llm(prompt_json)

            bid_amount = response.get("bid", 0)
            
            # Anti-cheat: AI cannot bid more than its liquid balance
            bid_amount = min(bid_amount, p.balance)

            if bid_amount > 0:
                bids[p.id] = bid_amount
                self.state.logs.append(f"{log_prefix} : {p.name} places a secret bid.")
            else:
                self.state.logs.append(f"{log_prefix} : {p.name} passes on the auction.")

        # 2. Resolve the auction
        if bids:
            # Find the highest bidder
            highest_bidder_id = max(bids, key=bids.get)
            winning_bid = bids[highest_bidder_id]
            winner = next(p for p in self.state.players if p.id == highest_bidder_id)

            winner.balance -= winning_bid
            space.owner_id = winner.id
            self.state.logs.append(f"{log_prefix} : 🏆 {winner.name} WINS the auction for {space.name} at ${winning_bid}! (Balance: ${winner.balance})")
        else:
            self.state.logs.append(f"{log_prefix} : No one bid. {space.name} remains unsold.")