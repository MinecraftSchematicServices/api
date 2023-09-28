from importlib import import_module, reload
import sys
import inspect
import os
import json
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from schematicGenerator.base_generator import BaseGenerator
from server.websocket_routes import queue


MAIN_PID = os.getpid()

known_generator_files = set()
generators_dict = {}
processed_files = set()

def load_generator(file_path):
    loaded_generators = []
    module_name = "schematicGenerator.generators." + os.path.basename(file_path)[:-3]
    current_pid = os.getpid()
    try:
        if module_name in sys.modules:
            print(f"[PID: {current_pid}] Reloading {module_name}")
            module = reload(sys.modules[module_name])
        else:
            print(f"[PID: {current_pid}] Loading {module_name}")
            module = import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseGenerator)
                and obj != BaseGenerator
            ):
                generators_dict[obj.__name__] = obj
                loaded_generators.append(obj.__name__)
    except Exception as e:
        print(f"Error loading {module_name}: {e}")
        
    if current_pid == MAIN_PID:
        print("Main process")
        websocket_payload ={
            "type": "reload" if module_name in sys.modules else "load",
            "generators": list(generators_dict.keys())
        }
        websocket_payload = json.dumps(websocket_payload)
        queue.put(websocket_payload)
    return loaded_generators


def unload_generator(file_path):
    module_name = "schematicGenerator.generators." + os.path.basename(file_path)[:-3]
    current_pid = os.getpid()
    print(f"[PID: {current_pid}] Unloading {module_name}")
    if module_name in sys.modules:
        module = sys.modules[module_name]
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseGenerator)
                and obj != BaseGenerator
            ):
                if obj.__name__ in generators_dict:
                    del generators_dict[obj.__name__]
        del sys.modules[module_name]
    if current_pid == MAIN_PID:
        print("Main process")
        websocket_payload ={
            "type": "delete",
            "generators": [k for k in generators_dict.keys()]
        }
        websocket_payload = json.dumps(websocket_payload)
        queue.put(websocket_payload)
    
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("Modified")
        global known_generator_files
        if event.is_directory and event.src_path.endswith("/generators"):
            current_files = set(glob.glob("./schematicGenerator/generators/*.py"))
            # for known_file in list(known_generator_files):
            #     if known_file not in current_files :
            #         print(f"Deleted file: {known_file} among {current_files}")
            #         unload_generator(known_file)
            #         known_generator_files.remove(known_file)
            
            # remove any files that are not in current_files
            files_to_remove = []
            for known_file in known_generator_files:
                if known_file not in current_files:
                    files_to_remove.append(known_file)
            for file in files_to_remove:
                # check if still in known files, because it might have been removed by on_deleted
                if file in known_generator_files:
                    print(f"Deleted file: {file} among {known_generator_files}")
                    unload_generator(file)
                    known_generator_files.remove(file)
            for file in current_files:
                if file not in known_generator_files:
                    print(f"New file: {file} among {known_generator_files}")
                    load_generator(file)
                    known_generator_files.add(file)
        elif not event.is_directory and event.src_path.endswith(".py") and event.src_path :
            print(f"Modified file: {event.src_path} among {known_generator_files}")
            load_generator(event.src_path)
            known_generator_files.add(event.src_path)

        

    def on_deleted(self, event):
        # global known_generator_files
        # print("Delete")
        # if not event.is_directory and event.src_path.endswith(".py"):
        #     unload_generator(event.src_path)
        #     known_generator_files.remove(event.src_path)
        files_to_remove = []
        for known_file in known_generator_files:
            if not os.path.exists(known_file):
                files_to_remove.append(known_file)
        for file in files_to_remove:
            if file in known_generator_files:
                print(f"Deleted file: {file} among {known_generator_files}")
                unload_generator(file)
                known_generator_files.remove(file)
            
observer = None

async def init_observer(app, loop):
    global observer
    observer = Observer()
    observer.schedule(FileChangeHandler(), path="./schematicGenerator/generators/", recursive=False)
    observer.start()
    print("Observer started")

async def stop_observer(app, loop):
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("Observer stopped")
        
def initialize_generators():
    for file in glob.glob("./schematicGenerator/generators/*.py"):
        known_generator_files.add(file)
        print("PID: ", os.getpid())
        load_generator(file)