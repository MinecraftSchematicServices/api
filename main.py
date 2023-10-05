from sanic import Sanic
from server.routes import list_generators, generate
from server.websocket_routes import feed
from hotloading.hotload_manager import init_observer, stop_observer, initialize_generators
from sanic_ext import Extend

app = Sanic(name="GeneratorsAPI")
app.config.CORS_ORIGINS = "*"
# Attach routes
app.add_route(list_generators, "/generators")
app.add_route(generate, "/generate/<generator_name>", methods=["POST"])
app.add_websocket_route(feed, "/ws")

app.listener('before_server_start')(init_observer)
app.listener('after_server_stop')(stop_observer)

initialize_generators()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
