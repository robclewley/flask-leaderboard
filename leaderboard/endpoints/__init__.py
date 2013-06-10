import pkgutil

from flask import g, session

from leaderboard import app
from leaderboard.database import User

__all__ = []
for (loader, module_name, is_pkg,) in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = module

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter(User.id == session['user_id']).first()