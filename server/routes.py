from sanic import response
from .websocket_routes import queue
from hotloading.hotload_manager import generators_dict
import mcschematic
import traceback
import concurrent.futures
class TimeoutException(Exception):
    pass

def run_generate(args):
    try:
        generator_class = generators_dict.get(args["generator_name"])
        schem = generator_class.generate(**args["request_args"])
        return schem
    except Exception as e:
        return e


async def list_generators(request):
    generators = {k: v.to_dict() for k, v in generators_dict.items()}
    return response.json(generators)

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
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_generate, {"generator_name": generator_name, "request_args": args})
        
        try:
            # Try to get the result within the timeout
            schem = future.result(timeout=20)

            if isinstance(schem, Exception):
                raise schem

            name = "test"
            schem.save("./generated_schems", name, mcschematic.Version.JE_1_19)
            return await response.file(
                "./generated_schems/" + name + ".schem",
                filename=name + ".schem",
                mime_type="application/octet-stream",
            )

        except concurrent.futures.TimeoutError:
            return response.json({"error": "Operation timed out"}, status=408)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return response.json({"error": str(e)}, status=400)