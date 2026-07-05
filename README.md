# Midea MCP Proxy

给 Claude 用的美的家电 MCP server。走美居云端账号控制美的家电。

## 部署步骤（Railway）

1. **推送本仓库到 GitHub**：`quandongchen221-alt/midea-mcp-proxy`
2. **Railway → New Project → Deploy from GitHub repo**
3. **添加环境变量**（Railway → Variables）：
   - `MIDEA_ACCOUNT` = 美居登录手机号
   - `MIDEA_PASSWORD` = 美居密码
   - `MIDEA_APP` = `美的美居`（大陆账号；国际版填 `MSmartHome`）
4. **拿到 Railway 分配的 URL**（形如 `https://xxx.up.railway.app`）
5. **在 Claude → Settings → Connectors → Add custom connector** 里，把 URL 后加 `/mcp` 填进去

## 可用工具

- `list_devices` — 列出账号下所有设备（先跑这个拿 device_id）
- `get_device_status` — 查设备状态
- `turn_on` / `turn_off` — 开关
- `set_fan_speed` — 调风速（1-3，不一定所有型号支持）

## 已知风险

- 蒸发式冷风扇（AAI12PV）不在 midea-beautiful-air 官方支持列表里
- 能否真控上，得部署完调 `list_devices` + `turn_on` 试
- 云端 API 偶尔变，控不动的话是美的改了协议
