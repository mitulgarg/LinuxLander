# schemas.py

from pydantic import BaseModel, Field
from typing import Optional


class TroubleshootingGuide(BaseModel):
    """A structured guide for troubleshooting a Linux error."""
    error_summary: str = Field(
        ...,  #ellipsis means this field is required
        description="A concise, one-sentence summary of the detected error."
    )
    suspected_cause: str = Field(
        ..., 
        description="The likely root cause of the error based on the log entries."
    )
    log_file_path: str = Field(
        ..., 
        description="The absolute path to the most relevant log file that was analyzed."
    )
    relevant_log_entry: str = Field(
        ..., 
        description="The specific log line or snippet that points to the error."
    )
    suggested_command: Optional[str] = Field(
        None, 
        description="A single, safe terminal command to help fix the issue. Should be non-destructive."
    )