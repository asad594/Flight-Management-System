from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib
import uuid
from core.framework import Router, TemplateEngine
import core.custom_views

# In-memory session store: {session_id: user_id}
SESSION_STORE = {}

class AppHandler(BaseHTTPRequestHandler):
    """Standalone multithreaded HTTP request handler serving template views and static assets."""

    def log_message(self, format, *args):
        # Keep the default logging
        super().log_message(format, *args)

    def get_session_user(self):
        """Parse cookies and return user_id from session store."""
        cookies = {}
        cookie_header = self.headers.get('Cookie', '')
        for part in cookie_header.split(';'):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k.strip()] = v.strip()
        session_id = cookies.get('skybound_session')
        if session_id and session_id in SESSION_STORE:
            return SESSION_STORE[session_id], session_id
        return None, None

    def build_request(self, path: str, query: dict, method: str, post_data: dict = None, user = None):
        """Constructs a mock Request object compatible with view functions."""
        return type('Request', (), {
            'path': path,
            'GET': query,
            'POST': post_data or {},
            'method': method,
            'user': user,
            'request': {
                'path': path,
                'GET': query,
                'POST': post_data or {}
            }
        })()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        raw_query = urllib.parse.parse_qs(parsed_path.query)
        query = {k: v[0] if len(v) == 1 else v for k, v in raw_query.items()}

        user_id, session_id = self.get_session_user()
        user = None
        if user_id:
            from core.custom_views import get_user_by_id
            user = get_user_by_id(user_id)

        handler_result = Router.match(path)
        if handler_result and handler_result[0]:
            handler, kwargs = handler_result
            try:
                request = self.build_request(path, query, 'GET', user=user)
                result = handler(request, **kwargs)

                if isinstance(result, dict) and result.get('redirect'):
                    self.send_response(302)
                    self.send_header('Location', result['redirect'])
                    if result.get('set_cookie'):
                        self.send_header('Set-Cookie', result['set_cookie'])
                    if result.get('clear_cookie'):
                        self.send_header('Set-Cookie', 'skybound_session=; Max-Age=0; Path=/')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                try:
                    self.wfile.write(str(result).encode('utf-8'))
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                    pass
            except Exception as e:
                import traceback
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"500 Error: {str(e)}\n\n{traceback.format_exc()}".encode('utf-8'))

        elif path.startswith('/static/'):
            import os
            file_path = os.path.join('core', path.strip('/'))
            if not os.path.exists(file_path):
                file_path = os.path.join('.', path.strip('/'))

            if os.path.exists(file_path):
                self.send_response(200)
                if file_path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif file_path.endswith('.png'):
                    self.send_header('Content-type', 'image/png')
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    self.send_header('Content-type', 'image/jpeg')
                elif file_path.endswith('.svg'):
                    self.send_header('Content-type', 'image/svg+xml')
                elif file_path.endswith('.ico'):
                    self.send_header('Content-type', 'image/x-icon')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Static File Not Found")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # RAW DATA MONITOR: See exactly what the browser sends!
        print(f"\n[RAW DATA RECEIVED]: {body}")

        # Standard Body Parsing
        post_data = urllib.parse.parse_qs(body)
        # Flatten single-value lists
        post_flat = {k: v[0] if len(v) == 1 else v for k, v in post_data.items()}

        user_id, session_id = self.get_session_user()
        user = None
        if user_id:
            from core.custom_views import get_user_by_id
            user = get_user_by_id(user_id)

        handler_result = Router.match(path)
        if handler_result and handler_result[0]:
            handler, kwargs = handler_result
            try:
                request = self.build_request(path, query, 'POST', post_data=post_flat, user=user)
                result = handler(request, **kwargs)

                if isinstance(result, dict) and result.get('redirect'):
                    self.send_response(302)
                    self.send_header('Location', result['redirect'])
                    if result.get('set_cookie'):
                        sid = str(uuid.uuid4())
                        SESSION_STORE[sid] = result['set_cookie']
                        self.send_header('Set-Cookie', f'skybound_session={sid}; Path=/; HttpOnly')
                    if result.get('clear_cookie'):
                        if session_id and session_id in SESSION_STORE:
                            del SESSION_STORE[session_id]
                        self.send_header('Set-Cookie', 'skybound_session=; Max-Age=0; Path=/')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                try:
                    self.wfile.write(str(result).encode('utf-8'))
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                    pass
            except Exception as e:
                import traceback
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"500 Error: {str(e)}\n\n{traceback.format_exc()}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def run(port=8081):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, AppHandler)
    print(f"SkyBound Custom Python Server running at http://localhost:{port}/")
    print("Zero external frameworks. Pure Python.")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
