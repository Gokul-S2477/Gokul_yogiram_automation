import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
import ctypes


def _resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base_dir = Path(__file__).resolve().parent
    return str(base_dir / relative_path)


def _log_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "launcher.log"
    return Path(__file__).resolve().parent / "launcher.log"


def _log(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _log_path().open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass


def _show_error(message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(0, message, "Pharma Forecast App", 0x10)
    except Exception:
        _log(f"Failed to show message box: {message}")


def _find_free_port(start: int = 8510, end: int = 8599) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    return 8501


def _open_browser(port: int) -> None:
    webbrowser.open(f"http://127.0.0.1:{port}")


def _wait_for_server(port: int, timeout_seconds: int = 90) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.5)
    return False


def _open_browser_when_ready(port: int) -> None:
    _log(f"Waiting for local server on port {port}")
    if _wait_for_server(port):
        _log(f"Server is ready on port {port}, opening browser")
        _open_browser(port)
        return

    log_file = _log_path()
    _log(f"Server did not become reachable on port {port}")
    _show_error(
        "The local app server did not start in time.\n\n"
        f"Please check: {log_file}"
    )


def main() -> None:
    app_script = _resource_path("app.py")
    port = _find_free_port()
    _log(f"Launcher started. app_script={app_script} port={port}")

    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_LOG_LEVEL", "info")

    from streamlit import config as streamlit_config
    from streamlit.web import bootstrap

    streamlit_options = {
        "server.port": port,
        "server.address": "127.0.0.1",
        "server.headless": True,
        "server.fileWatcherType": "none",
        "browser.gatherUsageStats": False,
        "global.developmentMode": False,
    }

    # Mirror `streamlit run` setup so packaged builds do not fall back to the
    # frontend development server on localhost:3000.
    streamlit_config._main_script_path = app_script
    bootstrap.load_config_options(flag_options=streamlit_options)
    _log(
        "Loaded Streamlit config: "
        f"developmentMode={streamlit_config.get_option('global.developmentMode')} "
        f"server.port={streamlit_config.get_option('server.port')} "
        f"server.address={streamlit_config.get_option('server.address')}"
    )

    browser_thread = threading.Thread(
        target=_open_browser_when_ready,
        args=(port,),
        daemon=True,
    )
    browser_thread.start()

    try:
        bootstrap.run(
            app_script,
            False,
            [],
            streamlit_options,
        )
    except Exception as exc:
        _log(f"Launcher failed: {exc!r}")
        _show_error(
            "The application could not start.\n\n"
            f"Error: {exc}\n\n"
            f"Log file: {_log_path()}"
        )
        raise


if __name__ == "__main__":
    main()
