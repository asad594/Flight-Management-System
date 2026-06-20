import sys
sys.path.append('.')
from core.custom_views import search_flights
from core.models import User
class Req: pass
r = Req()
r.user = User(1, 'a', 'a', 'a', 1)
r.GET = {'origin': 'Karachi', 'destination': 'Skardu'}
res = search_flights(r)
print('Skardu count:', res.count('Skardu'))
print('No national:', 'No national routes currently active' in res)
