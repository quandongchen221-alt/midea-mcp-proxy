"""
Midea MCP Server
Wraps midea-beautiful-air to expose Midea appliance control as MCP tools.
Deploys on Railway. Reads credentials from env vars.
"""

import os
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("midea-mcp")

MIDEA_ACCOUNT = os.getenv("MIDEA_ACCOUNT", "")
MIDEA_PASSWORD = os.getenv("MIDEA_PASSWORD", "")
# "美的美居" for mainland China accounts; "MSmartHome" for international.
MIDEA_APP = os.getenv("MIDEA_APP", "美的美居")

mcp = FastMCP("midea-mcp")

_cloud = None


def get_cloud():
    """Lazy-init cloud connection so import doesn't fail without env vars."""
    global _cloud
    if _cloud is not None:
        return _cloud
    if not MIDEA_ACCOUNT or not MIDEA_PASSWORD:
        raise RuntimeError("MIDEA_ACCOUNT / MIDEA_PASSWORD env vars not set")
    from midea_beautiful import connect_to_cloud
    _cloud = connect_to_cloud(
        account=MIDEA_ACCOUNT,
        password=MIDEA_PASSWORD,
        appname=MIDEA_APP,
    )
    log.info("Connected to Midea cloud as %s", MIDEA_ACCOUNT)
    return _cloud


@mcp.tool()
def list_devices() -> str:
    """List all Midea appliances bound to Cici's 美的美居 account.

    Returns id / name / type / model / online status for each device.
    Use this first to find the target device id before calling other tools.
    """
    try:
        cloud = get_cloud()
        devices = cloud.list_appliances()
        if not devices:
            return "账号下没有设备。"
        lines = []
        for d in devices:
            lines.append(
                f"id={d.get('id')} | name={d.get('name')} | "
                f"type={d.get('type')} | model={d.get('model')} | "
                f"online={d.get('onlineStatus')}"
            )
        return "\n".join(lines)
    except Exception as e:
        log.exception("list_devices failed")
        return f"Error: {e}"


@mcp.tool()
def get_device_status(device_id: str) -> str:
    """Get current state of a specific Midea device by its id."""
    try:
        from midea_beautiful import appliance_state
        cloud = get_cloud()
        appliance = appliance_state(cloud=cloud, appliance_id=device_id)
        return f"state = {appliance.state}"
    except Exception as e:
        log.exception("get_device_status failed")
        return f"Error: {e}"


@mcp.tool()
def turn_on(device_id: str) -> str:
    """Turn a Midea device ON by its id."""
    try:
        from midea_beautiful import appliance_state
        cloud = get_cloud()
        appliance = appliance_state(cloud=cloud, appliance_id=device_id)
        appliance.state.running = True
        appliance.apply()
        return f"设备 {device_id} 已开机"
    except Exception as e:
        log.exception("turn_on failed")
        return f"Error: {e}"


@mcp.tool()
def turn_off(device_id: str) -> str:
    """Turn a Midea device OFF by its id."""
    try:
        from midea_beautiful import appliance_state
        cloud = get_cloud()
        appliance = appliance_state(cloud=cloud, appliance_id=device_id)
        appliance.state.running = False
        appliance.apply()
        return f"设备 {device_id} 已关机"
    except Exception as e:
        log.exception("turn_off failed")
        return f"Error: {e}"


@mcp.tool()
def set_fan_speed(device_id: str, speed: int) -> str:
    """Set fan speed (1-3 typically). May not work on all fan models."""
    try:
        from midea_beautiful import appliance_state
        cloud = get_cloud()
        appliance = appliance_state(cloud=cloud, appliance_id=device_id)
        appliance.state.fan_speed = speed
        appliance.apply()
        return f"设备 {device_id} 风速设为 {speed}"
    except Exception as e:
        log.exception("set_fan_speed failed")
        return f"Error: {e}"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    log.info("Starting Midea MCP server on port %d", port)
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    # Railway proxies through its own domain; disable DNS rebinding check
    # so the Host header from *.up.railway.app is accepted.
    try:
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
    except Exception:
        pass
    mcp.run(transport="streamable-http")
