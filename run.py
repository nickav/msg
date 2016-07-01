import sys
# Run a test server.
from app import app
port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
app.run(debug=True, port=port)
