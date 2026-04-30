
from mcp_servers.base_server import BaseServer


class MathServer(BaseServer):
    def __init__(self,cmd_config):
        super().__init__(cmd_config,"MathServer", prefix="math")
        self.setup_server()

    def setup_server(self):
        @self.mcp_instance.tool
        def add(a: float, b: float) -> float:
            """Add two numbers."""
            return a + b

        @self.mcp_instance.tool
        def multiply(a: float, b: float) -> float:
            """Multiply two numbers."""
            return a * b

        @self.mcp_instance.tool
        def calculate_power(base: float, exponent: float) -> float:
            """Calculate base raised to the power of exponent."""
            return base ** exponent


