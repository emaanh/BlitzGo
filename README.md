# BlitzGo
BlitzGo is a board game created by Maxwell, Teo, and me. Inspired by the Chinese game Go, it features a much faster, more dynamic playstyle. The name "Blitz" comes from "Blitzkrieg," a World War II military tactic known for its speed and intensity, contrasting with the slower, more strategic pace of traditional Go.

Don't let the super simple rules of the game fool you. There is an immense depth of strategy and mathematical elegance that we have yet to uncover, making this game 'harder for an AI to play than other games like Go and Chess.' 

Play the game at https://www.BlitzGo.net

## Installation

Ensure you have Python 3.6 or later installed on your machine. Clone the repository and install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/emaanh/BlitzGo.git

# Navigate to the project directory
cd BlitzGo

# Install dependencies
pip install -r requirements.txt
```

## Rules

1) A stone can be placed in any tile
2) Territory is made by completing encirclements with stones
3) A stone placed within the opponents territory will be deleted in the following turn
4) A max of 2 walls can be used for encirclement.
5) Moves that revert previous states of the board are illegal 
6) Game ends when any placement of a new stone not in your territory cannot survive more than one turn.
7) The player with more territory wins
