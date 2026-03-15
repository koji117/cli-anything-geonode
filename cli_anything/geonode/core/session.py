"""Stateful session management for GeoNode CLI."""

import json
import time


class Session:
    """Manages stateful CLI session with connection context and history."""

    def __init__(self, url="http://localhost:8000", auth_type="token",
                 token=None, username=None, password=None):
        self.url = url
        self.auth_type = auth_type
        self.token = token
        self.username = username
        self.password = password
        self.history = []
        self.created = time.time()
        self.modified = time.time()

    def record_action(self, action, params, result=None):
        """Record an action in history."""
        entry = {
            "action": action,
            "params": params,
            "result": result,
            "timestamp": time.time(),
        }
        self.history.append(entry)
        self.modified = time.time()

    def to_dict(self):
        """Serialize session to dict."""
        return {
            "url": self.url,
            "auth_type": self.auth_type,
            "token": self.token,
            "username": self.username,
            "password": self.password,
            "history": self.history,
            "created": self.created,
            "modified": self.modified,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize session from dict."""
        s = cls(
            url=data.get("url", "http://localhost:8000"),
            auth_type=data.get("auth_type", "token"),
            token=data.get("token"),
            username=data.get("username"),
            password=data.get("password"),
        )
        s.history = data.get("history", [])
        s.created = data.get("created", time.time())
        s.modified = data.get("modified", time.time())
        return s

    def save(self, path):
        """Save session to file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path):
        """Load session from file."""
        with open(path, "r") as f:
            return cls.from_dict(json.load(f))

    def status(self):
        """Get session status dict."""
        return {
            "url": self.url,
            "auth_type": self.auth_type,
            "username": self.username or "(none)",
            "actions": len(self.history),
        }
