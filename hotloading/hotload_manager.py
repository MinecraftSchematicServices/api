from importlib import import_module, reload
import sys
import inspect
import os
import json
import glob
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from schematic_generator.base_generator import BaseGenerator
from server.websocket_routes import queue


MAIN_PID = os.getpid()

known_generator_files = set()
generators_dict = {}
processed_files = set()
LOAD = "load"
UNLOAD = "unload"
RELOAD = "reload"
DELETE = "delete"
MAIN_PID = os.getpid()

generators_dict = {} 

def get_module_name(file_path):
    """Return the module name based on the file path."""
    return "schematic_generator.generators." + os.path.relpath(file_path, "./schematic_generator/generators").replace("/", ".")[:-3]

def is_valid_generator(obj):
    """Check if the object is a valid generator."""
    return inspect.isclass(obj) and issubclass(obj, BaseGenerator) and obj != BaseGenerator

def load_module_members(module, loaded_generators=None):
    """Load module members into the generators dictionary."""
    if loaded_generators is None:
        loaded_generators = []

    for name, obj in inspect.getmembers(module):
        if is_valid_generator(obj):
            generators_dict[obj.__name__] = obj
            loaded_generators.append(obj.__name__)

    return loaded_generators

def unload_module_members(module):
    """Unload module members from the generators dictionary."""
    for name, obj in inspect.getmembers(module):
        if is_valid_generator(obj) and obj.__name__ in generators_dict:
            del generators_dict[obj.__name__]

def send_websocket_payload(action_type):
    """Send payload via websocket."""
    websocket_payload = {
        "type": action_type,
        "generators": list(generators_dict.keys())
    }
    queue.put(json.dumps(websocket_payload))

def load_generator(file_path):
    """Load or reload a generator module."""
    module_name = get_module_name(file_path)
    current_pid = os.getpid()
    loaded_generators = []
    try:
        if module_name in sys.modules:
            print(f"[PID: {current_pid}] Reloading {module_name}")
            module = reload(sys.modules[module_name])
            action_type = RELOAD
        else:
            print(f"[PID: {current_pid}] Loading {module_name}")
            module = import_module(module_name)
            action_type = LOAD

        loaded_generators = load_module_members(module, loaded_generators=loaded_generators)
        if current_pid == MAIN_PID:
            send_websocket_payload(action_type)
    except Exception as e:
        if module_name in sys.modules:
            del sys.modules[module_name]
        print(f"Error loading {module_name}: {e}")
        print(traceback.format_exc())
        # raise e
    

    return loaded_generators

def unload_generator(file_path):
    """Unload a generator module."""
    module_name = get_module_name(file_path)
    current_pid = os.getpid()
    print(f"[PID: {current_pid}] Unloading {module_name}")

    if module_name in sys.modules:
        module = sys.modules[module_name]
        unload_module_members(module)
        del sys.modules[module_name]

    if current_pid == MAIN_PID:
        send_websocket_payload(DELETE)

class FileChangeHandler(FileSystemEventHandler):
    
    @staticmethod
    def remove_files(files_to_remove):
        """Remove files from the known_generator_files and unload them."""
        for file in files_to_remove:
            print(f"Deleted file: {file} among {known_generator_files}")
            unload_generator(file)
            known_generator_files.remove(file)

    def on_modified(self, event):
        print("Modified")
        global known_generator_files
        current_files = set(glob.glob("./schematic_generator/generators/**/*.py", recursive=True))
        if event.is_directory and "./schematic_generator/generators" in event.src_path:
            
            files_to_remove = [known_file for known_file in known_generator_files if known_file not in current_files]
            self.remove_files(files_to_remove)
            
            for file in current_files:
                if file not in known_generator_files:
                    print(f"New file: {file} among {known_generator_files}")
                    load_generator(file)
                    known_generator_files.add(file)
                    
        elif not event.is_directory and event.src_path.endswith(".py"):
            file_path = "./" + os.path.relpath(event.src_path)
            if file_path not in current_files:
                print(f"Deleted file: {file_path} among {known_generator_files}")
                self.remove_files([file_path])
                return
            print(f"Modified file: {file_path} among {known_generator_files}")
            load_generator(file_path)
            known_generator_files.add(file_path)

    def on_deleted(self, event):
        files_to_remove = [known_file for known_file in known_generator_files if not os.path.exists(known_file)]
        self.remove_files(files_to_remove)

            
observer = None

async def init_observer(app, loop):
    global observer
    observer = Observer()
    observer.schedule(FileChangeHandler(), path="./schematic_generator/generators/", recursive=True)
    observer.start()
    print("Observer started")

async def stop_observer(app, loop):
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("Observer stopped")
        
def initialize_generators():
    # for file in glob.glob("./schematic_generator/generators/*.py"):
    # recursively look under the generators directory for python files
    for file in glob.glob("./schematic_generator/generators/**/*.py", recursive=True):
        known_generator_files.add(file)
        print("PID: ", os.getpid())
        load_generator(file)