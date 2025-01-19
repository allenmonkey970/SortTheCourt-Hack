import pymem
from pymem.process import module_from_name
import threading
import time

#Download link: https://graebor.itch.io/sort-the-court

# Initialize global variables
writing_enabled = False
stop_writing_event = threading.Event()

try:
    # Initialize Pymem and the game module
    pm = pymem.Pymem("SortTheCourt.exe")
    game_module = module_from_name(pm.process_handle, "mono.dll").lpBaseOfDll
except pymem.exception.ProcessNotFound as e:
    print("Could not find process: Game not open or installed")
    exit()
except Exception as e:
    print(f"Unexpected error: {e}")
    exit()


# Function to get pointer address
def get_ptr_addr(base, offsets):
    addr = pm.read_int(base)  # my addr is 44439536
    for offset in offsets[:-1]:
        addr = pm.read_int(addr + offset)
    return addr + offsets[-1]


# Function to get pointers
def get_ptrs():
    gold_ptr = get_ptr_addr(game_module + 0x001F30AC, [0x3C4, 0x68, 0x38, 0x5C, 0x70, 0xB0,0x0C])
    happiness_ptr = get_ptr_addr(game_module + 0x001F30AC, [0x548, 0x56C, 0x0C, 0x14, 0xD0, 0xB4, 0x0C])
    population_ptr = get_ptr_addr(game_module + 0x001F30AC, [0x548, 0x2C, 0x08, 0x56C, 0xD0, 0xB8, 0x0C])
    # tuple for pointers and their descriptions
    ptrs = (
        ("Gold Pointer", gold_ptr),
        ("Happiness Pointer", happiness_ptr),
        ("Population Pointer", population_ptr)
    )
    return ptrs


# Function to write value in a loop
def infinite_write(hack_ptrs):
    while not stop_writing_event.is_set():
        if writing_enabled:
            for name, ptr in hack_ptrs:
                try:
                    pm.write_int(ptr, 9999)
                except pymem.exception.MemoryWriteError as e:
                    print(f"Game closed: Error in main execution: {e}")
                    return
                except Exception as e:
                    print(f"Error in main execution: {e}")
                    return
        time.sleep(0.1)  # Prevent high CPU usage


# Function to toggle writing
def toggle_writing():
    global writing_enabled
    while True:
        input("Press Enter to toggle infinite writing...")
        writing_enabled = not writing_enabled
        print(f"Infinite writing {'enabled' if writing_enabled else 'disabled'}.")


if __name__ == '__main__':
    try:
        ptrs = get_ptrs()
        # Start the writing thread
        writing_thread = threading.Thread(target=infinite_write, args=(ptrs,))
        writing_thread.start()
        # Start the input listener thread
        toggle_thread = threading.Thread(target=toggle_writing)
        toggle_thread.start()
    except Exception as e:
        print(f"Error in main execution: {e}")
