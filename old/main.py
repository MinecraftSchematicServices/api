from sanic import Sanic, response, Websocket
from importlib import import_module, reload
import sys
import inspect
import glob
import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from schematic_generator.base_generator import BaseGenerator
import mcschematic
import asyncio
from multiprocessing import Queue

app = Sanic(name="GeneratorsAPI")
known_generator_files = set()
generators_dict = {}
queue = Queue()


def load_generator(file_path):
    loaded_generators = []
    module_name = "generators." + os.path.basename(file_path)[:-3]
    try:
        if module_name in sys.modules:
            print(f"Reloading {module_name}")
            module = reload(sys.modules[module_name])
        else:
            print(f"Importing {module_name}")
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
    websocket_payload ={
        "type": "reload",
        "generators": [k.to_dict() for k in generators_dict.values()]
    }
    websocket_payload = json.dumps(websocket_payload)
    queue.put(websocket_payload)
    return loaded_generators




for file in glob.glob("./generators/*.py"):
    known_generator_files.add(file)
    load_generator(file)


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global known_generator_files
        if event.is_directory and event.src_path.endswith("/generators"):
            current_files = set(glob.glob("./generators/*.py"))
            for known_file in known_generator_files:
                if known_file not in current_files:
                    unload_generator(known_file)
            for file in current_files:
                if file not in known_generator_files:
                    load_generator(file)

        elif not event.is_directory and event.src_path.endswith(".py"):
            load_generator(event.src_path)
        

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            unload_generator(event.src_path)


def unload_generator(file_path):
    module_name = "generators." + os.path.basename(file_path)[:-3]
    if file_path in known_generator_files:
        known_generator_files.remove("./generators/" + os.path.basename(file_path))
    print(f"Unloading {module_name}")
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
    websocket_payload ={
        "type": "reload",
        "generators": [k for k in generators_dict.keys()]
    }
    websocket_payload = json.dumps(websocket_payload)
    queue.put(websocket_payload)

observer = None

@app.listener('before_server_start')
async def init_observer(app, loop):
    global observer
    observer = Observer()
    observer.schedule(FileChangeHandler(), path="./generators/", recursive=False)
    observer.start()
    print("Observer started")

@app.listener('after_server_stop')
async def stop_observer(app, loop):
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("Observer stopped")
        

@app.websocket("/ws")
async def feed(request, ws):
    while True:
        if not queue.empty():
            await ws.send(queue.get())
        await asyncio.sleep(0.2)


@app.route("/generators")
async def list_generators(request):
    generators = [{k: v.to_dict()} for k, v in generators_dict.items()]
    return response.json(generators)


@app.route("/generate/<generator_name>", methods=["POST"])
async def generate(request, generator_name):
    # convert generator_name to class name 
    # e.g. circle-generator -> CircleGenerator
    generator_name = "".join(
        [word.capitalize() for word in generator_name.split("-")]
    )
    generator_class = generators_dict.get(generator_name)
    if not generator_class:
        return response.json(
            {"error": f"Generator {generator_name} not found"}, status=404
        )

    args = request.json
    try:
        schem = generator_class.generate(**args)
        name = "test"
        schem.save("./generated_schems", name, mcschematic.Version.JE_1_19)
        return await response.file(
            "./generated_schems/" + name + ".schem",
            filename=name + ".schem",
            mime_type="application/octet-stream",
        )
    except Exception as e:
        return response.json({"error": str(e)}, status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
