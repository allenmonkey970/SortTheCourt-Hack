# SortTheCourt Hack Script

This script modifies gold, happiness, and population values in the game [Sort The Court](https://graebor.itch.io/sort-the-court) using the Pymem library.

### Functions

- **`get_ptr_addr(base, offsets)`**: Calculates the address of a pointer based on a base address and a list of offsets.
- **`get_ptrs()`**: Retrieves and returns the pointer addresses for gold, happiness, and population values.
- **`infinite_write(hack_ptrs)`**: Continuously writes the value `9999` to specified addresses if writing is enabled.
- **`toggle_writing()`**: Toggles the writing mode on and off based on user input.

### Usage

1. Clone the repository.
2. Install dependencies with `pip install pymem`.
3. Run the script while the game is running.
4. Press Enter to toggle infinite writing mode.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
