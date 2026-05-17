from datetime import datetime, timezone
from uuid import uuid4
from werkzeug.utils import secure_filename


def safe_filename(filename: str) -> str:
    """Generate a safe filename and avoid collisions in the upload folder."""
    safe_name = secure_filename(filename)
    if not safe_name:
        safe_name = "resume"
    unique_id = uuid4().hex
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{timestamp}_{unique_id}_{safe_name}"
