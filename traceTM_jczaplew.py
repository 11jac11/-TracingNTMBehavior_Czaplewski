import csv
import sys
from typing import List, Tuple, Dict, Set
from collections import defaultdict

class TMConfig:
    def __init__(self, left_tape: str, state: str, head_char: str, right_tape: str, parent: int):
        self.left_tape = left_tape
        self.state = state
        self.head_char = head_char
        self.right_tape = right_tape
        self.parent = parent
    # Index of parent configuration in previous level
class TuringMachine:
    def __init__(self, filename: str):
        self.transitions = defaultdict(list)
        self.load_tm(filename)

    def load_tm(self, filename: str):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            self.name = next(reader)[0]  # Line 1: Machine name
            self.states = next(reader)    # Line 2: States
            self.sigma = next(reader)     # Line 3: Input alphabet
            self.gamma = next(reader)     # Line 4: Tape alphabet
            self.start_state = next(reader)[0]  # Line 5: Start state
            self.accept_state = next(reader)[0] # Line 6: Accept state
            self.reject_state = next(reader)[0] # Line 7: Reject state

            # Read transitions
            for row in reader:
                if len(row) == 5:  # Ensure valid transition
                    curr_state, read_char, next_state, write_char, direction = row
                    self.transitions[(curr_state, read_char)].append(
                        (next_state, write_char, direction))

    def run(self, input_str: str, max_depth: int = 1000) -> Tuple[bool, int, List[TMConfig]]:
        print(f"\nStarting with input: {input_str}")
        # Initialize configuration tree
        levels = []
        initial_config = TMConfig("", self.start_state, input_str[0] if input_str else "_",
                                input_str[1:] if len(input_str) > 1 else "", -1)
        levels.append([initial_config])

        total_transitions = 0

        for depth in range(max_depth):
            current_level = []

            # Process all configurations at current level
            for parent_idx, config in enumerate(levels[-1]):
                print(f"\nStep {depth}: State={config.state}, Head={config.head_char}, "
                      f"Left={config.left_tape}, Right={config.right_tape}")

                if config.state == self.accept_state:
                    print("Accepting configuration found!")
                    print(f"Total transitions made: {total_transitions}")
                    path = self.reconstruct_path(levels, len(levels)-1, parent_idx)
                    return True, depth, path

                if config.state == self.reject_state:
                    print("String rejected!")
                    print(f"Total transitions made: {total_transitions}")
                    continue

                # Get possible transitions
                possible_moves = self.transitions.get(
                    (config.state, config.head_char), [])
                print(f"Possible moves from ({config.state}, {config.head_char}): {possible_moves}")

                total_transitions += len(possible_moves) or 1

                # If no valid transitions, implicit reject
                if not possible_moves:
                    print(f"Total transitions made: {total_transitions}")
                    current_level.append(TMConfig(
                        config.left_tape, self.reject_state,
                        config.head_char, config.right_tape, parent_idx))
                    continue

                # Process each possible transition
                for next_state, write_char, direction in possible_moves:
                    new_config = self.make_move(config, next_state,
                                              write_char, direction, parent_idx)
                    current_level.append(new_config)

            if not current_level:
                # All paths rejected
                return False, depth, []

            levels.append(current_level)

            # Check if all configurations are in reject state
            if all(c.state == self.reject_state for c in current_level):
                return False, depth, []

        return None, max_depth, []  # Exceeded max depth

    def make_move(self, config: TMConfig, next_state: str,
                  write_char: str, direction: str, parent_idx: int) -> TMConfig:
        new_left = config.left_tape
        new_right = config.right_tape

        # Write character to current position
        if direction == 'R':
            new_left = new_left + write_char
            new_head = new_right[0] if new_right else '_'
            new_right = new_right[1:] if new_right else ''
        else:  # direction == 'L'
            new_right = write_char + new_right
            new_head = new_left[-1] if new_left else '_'
            new_left = new_left[:-1] if new_left else ''

        return TMConfig(new_left, next_state, new_head, new_right, parent_idx)

    def reconstruct_path(self, levels: List[List[TMConfig]],
                        level: int, config_idx: int) -> List[TMConfig]:
        path = []
        while level >= 0:
            config = levels[level][config_idx]
            path.append(config)
            config_idx = config.parent
            level -= 1
        return list(reversed(path))

def main():
    if len(sys.argv) != 3:
        print("Usage: python traceTM_jczaplew.py <tm_file> <input_string>")
        sys.exit(1)

    tm_file = sys.argv[1]
    input_str = sys.argv[2]
    tm = TuringMachine(tm_file)

    max_depth = 1000

    # Run the TM
    accepted, depth, path = tm.run(input_str, max_depth)

    # Add explicit console output
    print("\nFinal Result:")
    if accepted is None:
        print(f"Execution stopped after {max_depth} steps")
    elif accepted:
        print(f"String ACCEPTED in {depth} steps")
    else:
        print(f"String REJECTED in {depth} steps")

    # Write output to file
    with open('output.txt', 'w') as f:
        f.write(f"Machine: {tm.name}\n")
        f.write(f"Input: {input_str}\n")

        if accepted is None:
            f.write(f"Execution stopped after {max_depth} steps\n")
        elif accepted:
            f.write(f"String accepted in {depth} steps\n")
            f.write("\nExecution path:\n")
            for config in path:
                f.write(f"({config.left_tape}, {config.state}, "
                       f"{config.head_char}, {config.right_tape})\n")
        else:
            f.write(f"String rejected in {depth} steps\n")
if __name__ == "__main__":
    main()
