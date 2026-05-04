from dataclasses import dataclass
import os


def _resolve_cert_path(path: str) -> str:
    """Resolve certificate path relative to project root if it's relative.
    
    Project root is the parent directory of the fog/ package.
    If the path is absolute or the file exists in cwd, use it as-is.
    Otherwise, try to find it in the project root.
    """
    if os.path.isabs(path):
        return path
    
    # Check if file exists in current working directory
    if os.path.exists(path):
        return path
    
    # Project root is parent of fog/ package
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resolved_path = os.path.join(project_root, path)
    
    return resolved_path


@dataclass(frozen=True)
class FogConfig:
    serial_device: str = os.getenv("FOG_SERIAL_DEVICE", os.getenv("FOG_RFCOMM_DEVICE", "/dev/ttyACM0"))
    serial_baud: int = int(os.getenv("FOG_SERIAL_BAUD", os.getenv("FOG_RFCOMM_BAUD", "9600")))
    reconnect_seconds: float = float(os.getenv("FOG_RECONNECT_SECONDS", "3.0"))

    ingest_poll_seconds: float = float(os.getenv("FOG_INGEST_POLL_SECONDS", "0.1"))
    focus_update_seconds: float = float(os.getenv("FOG_FOCUS_UPDATE_SECONDS", "2.0"))
    display_update_seconds: float = float(os.getenv("FOG_DISPLAY_UPDATE_SECONDS", "1.0"))
    session_tick_seconds: float = float(os.getenv("FOG_SESSION_TICK_SECONDS", "1.0"))

    session_minutes: int = int(os.getenv("FOG_SESSION_MINUTES", "25"))
    break_minutes: int = int(os.getenv("FOG_BREAK_MINUTES", "5"))

    sqlite_path: str = os.getenv("FOG_SQLITE_PATH", "focusflow_mvp.db")

    aws_iot_enabled: bool = os.getenv("FOG_AWS_IOT_ENABLED", "true").lower() in ("true", "1", "yes")
    aws_iot_endpoint: str = os.getenv("FOG_AWS_IOT_ENDPOINT", "a1vd9v79ssqr0b-ats.iot.eu-west-2.amazonaws.com")
    aws_iot_region: str = os.getenv("FOG_AWS_IOT_REGION", os.getenv("AWS_REGION", "eu-west-2"))
    aws_iot_topic_prefix: str = os.getenv("FOG_AWS_IOT_TOPIC_PREFIX", "focusflow")
    aws_iot_publish_seconds: float = float(os.getenv("FOG_AWS_IOT_PUBLISH_SECONDS", "2.0"))
    aws_iot_cert_path: str = _resolve_cert_path(os.getenv("FOG_AWS_IOT_CERT_PATH", "raspberry-1-central.cert.pem"))
    aws_iot_key_path: str = _resolve_cert_path(os.getenv("FOG_AWS_IOT_KEY_PATH", "raspberry-1-central.private.key"))
    aws_iot_root_ca_path: str = _resolve_cert_path(os.getenv("FOG_AWS_IOT_ROOT_CA_PATH", "root-CA.crt"))
    aws_iot_client_id: str = os.getenv("FOG_AWS_IOT_CLIENT_ID", "focusflow-fog")

    rpc_host: str = os.getenv("FOG_RPC_HOST", "0.0.0.0")
    rpc_port: int = int(os.getenv("FOG_RPC_PORT", "5005"))