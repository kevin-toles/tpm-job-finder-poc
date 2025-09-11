import json

class CentralLogger:
    def __init__(self, name=None, log_file=None, cloud_hook=None, **kwargs):
        self.name = name
        self.log_file = log_file
        self.cloud_hook = cloud_hook
        
    def _write_log(self, level, msg, **kwargs):
        log_data = {
            "name": self.name,
            "level": level,
            "message": msg,
            **kwargs
        }
        
        # Write to file if specified
        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_data) + "\n")
                
        # Call cloud hook if specified
        if self.cloud_hook:
            self.cloud_hook(level.lower(), msg, kwargs)
            
        print(f"{level}: {msg} {kwargs}")
        
    def log(self, msg, **kwargs):
        self._write_log("LOG", msg, **kwargs)
        
    def info(self, msg, **kwargs):
        self._write_log("INFO", msg, **kwargs)
        
    def error(self, msg, **kwargs):
        self._write_log("ERROR", msg, **kwargs)

class StructuredFormatter:
    def format(self, msg):
        return f"[STRUCTURED] {msg}"
