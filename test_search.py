"""
Standalone Integration Test: Verifies custom template rendering and search flight query handling.
"""
import sys
sys.path.append('.')
from core.custom_views import search_flights
from core.models import User

class Req: 
    pass

r = Req()
r.user = User(1, 'admin', 'admin@skybound.com', 'pass', 1)
r.GET = {'origin': 'Karachi', 'destination': 'Dubai'}
res = search_flights(r)

assert isinstance(res, str), "search_flights should return rendered HTML string"
print("Test search_flights executed successfully. Rendered output length:", len(res))

