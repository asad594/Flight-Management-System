import re
import os

class TemplateEngine:
    @staticmethod
    def render(template_path, context=None):
        if context is None:
            context = {}
            
        with open(f"core/templates/{template_path}", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Handle extends
        extends_match = re.search(r'{%\s*extends\s*[\'"](.*?)[\'"]\s*%}', content)
        if extends_match:
            base_template = extends_match.group(1)
            content = re.sub(r'{%\s*extends\s*.*?%}', '', content)
            
            # Extract blocks
            blocks = {}
            for block_match in re.finditer(r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}', content, re.DOTALL):
                blocks[block_match.group(1)] = block_match.group(2)
                
            # Read base
            with open(f"core/templates/{base_template}", "r", encoding="utf-8") as f:
                base_content = f.read()
                
            # Replace blocks in base
            for block_name, block_content in blocks.items():
                base_content = re.sub(fr'{{%\s*block\s+{block_name}\s*%}}.*?{{%\s*endblock\s*%}}', block_content, base_content, flags=re.DOTALL)
            
            # Remove remaining unfilled blocks
            base_content = re.sub(r'{%\s*block\s+\w+\s*%}.*?{%\s*endblock\s*%}', '', base_content, flags=re.DOTALL)
            content = base_content

        # Handle {% for ... %} ... {% empty %} ... {% endfor %}
        def for_replacer(match):
            item_name = match.group(1).strip()
            list_name = match.group(2).strip()
            inner_content = match.group(3)
            
            # Check for {% empty %}
            empty_content = ""
            if '{% empty %}' in inner_content:
                parts = inner_content.split('{% empty %}')
                inner_content = parts[0]
                empty_content = parts[1]
                
            items = []
            if list_name.startswith('"') or list_name.startswith("'"):
                items = list(list_name[1:-1])
            else:
                items = context.get(list_name, [])
                
            if not items:
                return empty_content
                
            result = ""
            for item in items:
                item_html = inner_content
                
                # Replace {{ item.property.subprop }} and {{ item.property|filter }}
                def prop_replacer(m):
                    full_prop = m.group(1).strip()
                    parts = full_prop.split('|')[0].split('.')
                    filter_str = m.group(3) if m.lastindex >= 3 else None
                    
                    val = item
                    for part in parts:
                        val = getattr(val, part, '') if hasattr(val, part) else (val.get(part, '') if isinstance(val, dict) else '')
                        if val == '': break
                    
                    if filter_str:
                        if 'date:' in filter_str or 'date' in filter_str:
                            return str(val).split()[0] if val else ''
                    return str(val)
                    
                item_html = re.sub(fr'{{{{\s*{item_name}\.([a-zA-Z0-9_.]+)(\|(.*?))?\s*}}}}', prop_replacer, item_html)
                
                # Replace {% url 'book_flight' item.id %} inside loop
                def url_in_loop_replacer(m):
                    name = m.group(1)
                    val_str = m.group(2).strip()
                    if val_str.startswith(f"{item_name}."):
                        prop_path = val_str[len(item_name)+1:]
                        val = item
                        for part in prop_path.split('.'):
                            val = getattr(val, part, '') if hasattr(val, part) else (val.get(part, '') if isinstance(val, dict) else '')
                        if name == 'book_flight': return f"/book/{val}/"
                    return m.group(0) # Keep for global replacer if not matched
                
                item_html = re.sub(r"{%\s*url\s+['\"](\w+)['\"]\s+(.*?)\s*%}", url_in_loop_replacer, item_html)
                result += item_html
            return result
            
        content = re.sub(r'{%\s*for\s+(\w+)\s+in\s+([a-zA-Z0-9_"\']+)\s*%}(.*?){%\s*endfor\s*%}', for_replacer, content, flags=re.DOTALL)

        # Handle {% if %} ... {% else %} ... {% endif %}
        def if_replacer(match):
            condition_var = match.group(1).strip()
            inner_content = match.group(2)

            # Extract {% else %} if present
            else_content = ""
            if '{% else %}' in inner_content:
                parts = inner_content.split('{% else %}', 1)
                inner_content = parts[0]
                else_content = parts[1]

            val = False
            user = context.get('user')
            if condition_var == 'user.is_staff':
                val = bool(getattr(user, 'is_staff', False))
            elif condition_var in ('user.is_authenticated', 'user'):
                val = bool(user)
            elif '==' in condition_var:
                # Basic equality: booking.status == 'Confirmed'
                left, right = [s.strip().strip("'\"") for s in condition_var.split('==', 1)]
                val = (left == right)
            elif condition_var.startswith('request.path =='):
                path = condition_var.split('==')[-1].strip().strip("'\"")
                req_obj = context.get('request')
                val = (getattr(req_obj, 'path', '') == path) if req_obj else False
            elif condition_var in context:
                val = bool(context[condition_var])
            elif '.' in condition_var:
                # e.g. forloop.counter — just skip
                val = False

            return inner_content if val else else_content

        content = re.sub(r'{%\s*if\s+(.*?)\s*%}(.*?){%\s*endif\s*%}', if_replacer, content, flags=re.DOTALL)

        # Handle simple variables with optional pipes e.g. {{ request.GET.origin }}
        def var_replacer(m):
            full_var = m.group(1).strip()
            parts = full_var.split('|')[0].split('.')
            base = parts[0]
            
            if base == 'request':
                req_obj = context.get('request')
                if not req_obj: return ""
                if len(parts) > 1:
                    # Handle request.path, request.GET.something, etc.
                    attr = parts[1]
                    if attr == 'GET' and len(parts) > 2:
                        return str(getattr(req_obj, 'GET', {}).get(parts[2], ''))
                    return str(getattr(req_obj, attr, ''))
                return ""
            
            val = context.get(base, '')
            if len(parts) > 1 and val:
                for part in parts[1:]:
                    val = getattr(val, part, '') if hasattr(val, part) else (val.get(part, '') if isinstance(val, dict) else '')
            
            if '|length' in full_var:
                return str(len(val)) if isinstance(val, (list, tuple, dict, str)) else '0'
            if '|date' in full_var:
                # Basic mock for date filter
                return str(val).split()[0] if val else ''
            return str(val)
            
        content = re.sub(r'{{\s*(.*?)\s*}}', var_replacer, content)

        # Handle {% url 'name' %}
        url_map = {
            'home': '/',
            'about': '/about/',
            'contact': '/contact/',
            'register': '/register/',
            'login': '/login/',
            'logout': '/logout/',
            'search': '/search/',
            'my_bookings': '/my-bookings/',
            'admin_dashboard': '/admin-dashboard/',
            'admin_fleet': '/admin-fleet/',
            'admin_bookings': '/admin-bookings/',
            'admin_users': '/admin-users/',
            'admin_messages': '/admin-messages/',
        }
        for name, path in url_map.items():
            content = re.sub(fr"{{%\s*url\s+['\"]{name}['\"]\s*%}}", path, content)

        # Handle dynamic url {% url 'book_flight' flight.id %}
        def dynamic_url_replacer(match):
            name = match.group(1)
            val_str = match.group(2).strip()
            # Try to resolve val_str from context
            parts = val_str.split('.')
            base = parts[0]
            val = context.get(base, '')
            if len(parts) > 1 and val:
                for part in parts[1:]:
                    val = getattr(val, part, '') if hasattr(val, part) else (val.get(part, '') if isinstance(val, dict) else '')
            
            if name == 'book_flight':
                return f"/book/{val}/"
            return "#"

        content = re.sub(r"{%\s*url\s+['\"](\w+)['\"]\s+(.*?)\s*%}", dynamic_url_replacer, content)
        print(f"DEBUG: Rendered links search: {'/search/' in content}, about: {'/about/' in content}")

        # Remove load static
        content = re.sub(r'{%\s*load static\s*%}', '', content)
        
        # Handle {% static 'path' %}
        content = re.sub(r"{%\s*static\s+['\"](.*?)['\"]\s*%}", r"/static/\1", content)
        
        # Handle {% now 'Y-m-d' %}
        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d")
        content = re.sub(r"{%\s*now\s+['\"]Y-m-d['\"]\s*%}", now_str, content)
        
        return content

class Router:
    routes = {}

    @classmethod
    def add(cls, path, handler):
        cls.routes[path] = handler

    @classmethod
    def match(cls, path):
        path = path.split('?')[0]
        
        # Try exact and then flexible
        for route_path, handler in cls.routes.items():
            pattern = route_path
            if '<int:' in pattern:
                # Extract param name: <int:id> -> id
                param_match = re.search(r'<int:(\w+)>', pattern)
                if not param_match: continue
                param_name = param_match.group(1)
                pattern = re.sub(r'<int:\w+>', r'([0-9]+)', pattern)
                
                # Make trailing slash optional
                pattern = pattern.rstrip('/') + '/?'
                pattern = '^' + pattern + '$'
                
                match = re.match(pattern, path)
                if match:
                    val = int(match.group(1))
                    return handler, {param_name: val}
            else:
                # Static route
                pattern = pattern.rstrip('/') + '/?'
                pattern = '^' + pattern + '$'
                if re.match(pattern, path):
                    return handler, {}
                    
        return None, {}
