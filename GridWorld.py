import random
import json
import copy

# Class Representing GridWorld
class GridWorld:

	def __init__(self, grid_size):
		self.placed_words = []
		self.total_points = 0
		self.size = grid_size
		self.generate_blank_grid()

	def generate_blank_grid(self):
		new_grid = []
		for i in range(self.size):
			l = []
			for j in range(self.size):
				l.append(" ")
			new_grid.append(l)
		self.grid = new_grid

	def print_grid_solution(self):
		self.print_grid(self.grid)

	def print_grid(self, grid):
		print("-" * (len(grid[0]) * (len(grid[0][0]) + 1) + 1))
		for i in grid:
			row = "|"
			for j in i:
				row += j + "|"
			print(row)
		print("-" * (len(grid[0]) * (len(grid[0][0]) + 1) + 1))

	def print_grid_game(self):

		# Mark start locations and Expand
		grid = copy.deepcopy(self.grid)
		visible_index = {}
		for i in range(len(grid)):
			for j in range(len(grid[i])):
				if grid[i][j] != " ":
					isStart = False
					index = 0
					for k in self.placed_words:
						if k.row == i and k.col == j:
							if index < 10:
								grid[i][j] = "0" +  str(index)
							else:
								grid[i][j] = str(index)
							visible_index[str(i) + str(j)] = index
							isStart = True
							break
						index += 1

					if not isStart:
						grid[i][j] = "██"
				else:
					grid[i][j] = "  "

		# clean board rows
		tmp = []
		for i in grid:
			isEmpty = True
			for j in i:
				if j != "  ":
					isEmpty = False
			if isEmpty:
				tmp.append(i)
		for t in tmp:
			grid.remove(t)

		# clean board columns
		tmp.clear()
		col_size = len(grid[0])
		for i in range(col_size):
			isEmpty = True
			for j in range(len(grid)):
				if grid[j][i] != "  ":
					isEmpty = False
			if isEmpty:
				tmp.append(i)
		tmp.reverse()
		for t in tmp:
			for k in range(len(grid)):
				del grid[k][t]

		# Print solution grid
		self.print_grid(grid)

		# Print Hints
		print("--- Numbers are meant to be filled in too ---")
		for w in self.placed_words:
			index = visible_index[str(w.row) + str(w.col)]
			l = str(index) 
			if w.direction == "DOWN":
				l += " (DOWN) "
			else:
				l += " (ACCROSS) "
			l +=": "
			l += str(len(w.word)) + " letter word, " 
			l += w.hint
			print(l) 

	def get_cell(self, placement, offset):
		row = placement.row
		col = placement.col

		try:
			if placement.direction == "DOWN":
				return self.grid[row + offset][col]
			elif placement.direction == "RIGHT":
				return self.grid[row][col + offset]
			else:
				print("Error - placement does not have direction")
		except IndexError:
			return None

	def get_border(self, placement, atStart):
		row = placement.row
		col = placement.col
		border_letters = []

		try: 
			if not atStart:
				if placement.direction == "DOWN":
					row += (len(placement.word) - 1)
					border_letters.append(self.grid[row - 1][col]) # LEFT 
				elif placement.direction == "RIGHT":
					col += (len(placement.word) - 1)
					border_letters.append(self.grid[row][col - 1]) # UP

				border_letters.append(self.grid[row + 1][col]) # RIGHT
				border_letters.append(self.grid[row][col + 1]) # DOWN

			else:
				if placement.direction == "DOWN":
					border_letters.append(self.grid[row + 1][col]) # RIGHT
				elif placement.direction == "RIGHT":
					border_letters.append(self.grid[row][col + 1]) # DOWN

				border_letters.append(self.grid[row][col - 1]) # UP
				border_letters.append(self.grid[row - 1][col]) # LEFT
		except IndexError:
			print("Border Word Found")

		return border_letters

	def insert_placement(self, placement):
		self.placed_words.append(placement)
		self.total_points += placement.points

		if placement.direction == "RIGHT":
			for c in range(len(placement.word)):
				self.grid[placement.row][placement.col + c] = placement.word[c]
		else:
			for c in range(len(placement.word)):
				self.grid[placement.row + c][placement.col] = placement.word[c]


# Class For Possible Places
class GridPlacement:

	# Point Distributions
	encourage_vowel =  True
	encourage_vowel_point = 0.15

	encourage_middle_placement = True
	encourage_middle_placement_point = 0.50

	discourage_border_start = True
	discourage_border_start_point = 0.20

	discourage_border_end = True
	discourage_border_end_point = 0.25

	def __init__(self):
		self.word = ""
		self.hint = ""
		self.direction = ""
		self.row = 0
		self.col = 0
		self.points = 0
		self.isConflict = False	

	def calculate_points(self, gridWorld):

		# Check starting point is within range
		if (self.row < 0 or self.col < 0 or
				self.col > gridWorld.size or self.row > gridWorld.size):
			self.isConflict = True
			return

		# If the word hits the edges, then its in conflict
		if self.direction == "RIGHT":
			if len(self.word) + self.col >= gridWorld.size:
				self.isConflict = True
				return
		else:
			if len(self.word) + self.row >= gridWorld.size:
				self.isConflict = True
				return

		for letter_index in range(len(self.word)):

			world_cell_value = gridWorld.get_cell(self, letter_index)
			if world_cell_value == None:
				self.isConflict = True
				return

			if world_cell_value != " ":
				if self.word[letter_index] == world_cell_value:
					
					# Letter match
					self.points += 1

					# Encourage vowels
					if self.encourage_vowel :
						if (self.word[letter_index] in 
							 ['a', 'e', 'i', 'o', 'u']):
							self.points += self.encourage_vowel_point

					# Encourage middle placement
					if self.encourage_middle_placement:
						self.points += self.encourage_middle_placement_point * (letter_index / int(len(self.word)))

				else:
					self.isConflict = True
					return

		# Discourage words that start bordered by others
		if self.discourage_border_start:
			border_letters = gridWorld.get_border(self, True)
			for letter in border_letters:
				if letter != " ":
					self.points -= self.discourage_border_start_point

		# Discourage words that end bordered by others
		if self.discourage_border_end:
			border_letters = gridWorld.get_border(self, False)
			for letter in border_letters:
				if letter != " ":
					self.points -= self.discourage_border_end_point


# handles reading from the json dictionary
class CrossWordDict:

	file_path = "./dictionary/dictionary.json"
	max_word_size = 12
	min_word_size = 2
	data = None

	def __init__(self):
		print("Reading dictionary...")
		with open(self.file_path) as json_data:
			self.data = json.load(json_data)
			print("Dictionary read")

	def select_random(self, number_of_words):
		
		ret = []
		indexes = []
		keys = list(self.data.keys())
		
		while len(ret) < number_of_words:
			index = random.randint(0, len(self.data))
			if index in indexes:
				continue

			wordkey = keys[index]

			if wordkey.isalpha() and self.min_word_size < len(wordkey) < self.max_word_size:
				definition = self.data[wordkey]
				ret.append((wordkey.lower(), definition))

		return ret


# Insert Initial word
def place_initial_word(word, world):
	placement = GridPlacement()
	placement.word = word[0]
	placement.hint = word[1]
	placement.direction = "RIGHT"
	placement.row = int(world.size / 2)
	placement.col = placement.row - int(len(word) / 2)

	world.insert_placement(placement)

# Find matches in the grid
def find_letter_match(word_and_hint, world):
	word = word_and_hint[0]
	matches = []
	for i in range(len(world.placed_words)):
		curr_word = world.placed_words[i].word

		for j in range(len(word)):
			for k in range(len(curr_word)):
				
				if word[j] == curr_word[k]:

					obj = GridPlacement()
					obj.word = word
					obj.hint = word_and_hint[1]

					if world.placed_words[i].direction == "RIGHT":
						obj.direction = "DOWN"
						obj.row = world.placed_words[i].row - j
						obj.col = world.placed_words[i].col + k
					else:
						obj.direction = "RIGHT"
						obj.row = world.placed_words[i].row + j
						obj.col = world.placed_words[i].col - k
					matches.append(obj)

	return matches

# Insert as new word into the grid
def add_word_to_grid(word, world):
	if len(world.placed_words) == 0:
		place_initial_word(word, world)

	else:
		possible_matches = []
		for index in range(len(world.placed_words) - 1, -1, -1):

			placed_word = world.placed_words[index]
			matches = find_letter_match(word, world)

			if len(matches) == 0 :
				continue

			clean = []
			for match in matches:
				match.calculate_points(world)
				if match.isConflict == False:
					clean.append(match)
			possible_matches.extend(clean)

		if len(possible_matches) > 0:
			best_match = possible_matches[0]
			for match in possible_matches:
				if match.points > best_match.points:
					best_match = match

			world.insert_placement(best_match)


def main():
	# Get word list
	word_count = 20
	dictionary = CrossWordDict()
	word_list_and_hints = dictionary.select_random(word_count)

	# Get number of grids to generate
	num_grids = 1

	# Get grid Size
	size = 40

	# Generate grids
	grids = []
	for x in range(num_grids):

		# Shuffle the word list
		random.shuffle(word_list_and_hints)

		# Create and new grid and add the words
		grid = GridWorld(size)
		for word in word_list_and_hints:
			add_word_to_grid(word, grid)
		grids.append(grid)

	# Select grid with most points
	if len(grids) == 0:
		print("No grids could be generated")
		return

	best_grid = grids[0]
	for grid in grids:
		if best_grid.total_points < grid.total_points:
			best_grid = grid

	# Save grid
	best_grid.print_grid_solution()
	best_grid.print_grid_game()

if __name__ == "__main__":
    main()