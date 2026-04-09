# 飞书（Feishu / Lark）集成配置指南

## 前置要求

必须使用**自建应用**（Custom App），不支持商店应用（Store App）。

在 [飞书开放平台](https://open.feishu.cn/app) 或 [Lark 国际版](https://open.larksuite.com/) 创建自建应用。

---

## 一、飞书开放平台配置

### 1. 获取凭证

应用后台 → **凭证与基本信息** → 复制：
- App ID（格式：`cli_xxxxxxxxxxxxxxxx`）
- App Secret

### 2. 开启 Bot 能力

应用后台 → **应用功能** → 开启「机器人」

### 3. 添加权限

应用后台 → **权限管理** → 添加以下权限：

| 权限 | 是否必须 | 用途 |
|------|---------|------|
| `im:message` | 必须 | 接收消息 |
| `im:message:send_as_bot` | 必须 | 发送消息 |
| `im:resource` | 推荐 | 接收图片/文件 |
| `application:application:self_manage` | 推荐 | Bot 身份识别，消除启动警告 |
| `card.action.trigger` | 可选 | 支持交互卡片 |

### 4. 订阅事件（WebSocket 模式必须）

应用后台 → **事件订阅** → 添加：
- `im.message.receive_v1`（接收消息）

### 5. 发布应用

每次修改权限或事件订阅后，必须**创建新版本并发布**，否则变更不生效。

---

## 二、环境变量配置（`.env`）

### 必填

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
```

### 常用可选项

```bash
# 部署区域：feishu（国内）或 lark（国际），默认 feishu
FEISHU_DOMAIN=feishu

# 连接方式：websocket（推荐）或 webhook，默认 websocket
FEISHU_CONNECTION_MODE=websocket

# 用户白名单（逗号分隔的 open_id），未设置时需配合 GATEWAY_ALLOW_ALL_USERS
# FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy

# 定时任务输出的目标会话
# FEISHU_HOME_CHANNEL=oc_xxx

# Bot 身份（未配置 application:application:self_manage 权限时手动指定）
# FEISHU_BOT_NAME=your_bot_name
# FEISHU_BOT_OPEN_ID=ou_xxx
```

### Webhook 模式额外配置

```bash
FEISHU_CONNECTION_MODE=webhook
FEISHU_ENCRYPT_KEY=your_encrypt_key
FEISHU_VERIFICATION_TOKEN=your_token
FEISHU_WEBHOOK_HOST=127.0.0.1   # 默认
FEISHU_WEBHOOK_PORT=8765         # 默认
FEISHU_WEBHOOK_PATH=/feishu/webhook  # 默认
```

### 群组策略

```bash
# allowlist（默认）：仅白名单用户可触发
# open：所有人可触发
# disabled：禁用群组响应
FEISHU_GROUP_POLICY=allowlist
```

---

## 三、启动

```bash
hermes gateway
```

连接成功时日志显示：
```
[Feishu] Connected via WebSocket
```

---

## 四、常见错误排查

| 错误 | 原因 | 解决方法 |
|------|------|---------|
| `1000040347: store apps are not supported yet` | 使用了商店应用 | 重建为自建应用 |
| `Unable to hydrate bot identity` | 缺少身份识别权限 | 添加 `application:application:self_manage` 权限，或手动设置 `FEISHU_BOT_NAME` |
| 机器人不响应 | 权限/事件未生效 | 检查是否已发布新版本 |
| 群组中不响应 | 白名单限制 | 检查 `FEISHU_GROUP_POLICY` 和 `FEISHU_ALLOWED_USERS` |
| 收不到图片/文件 | 缺少权限 | 添加 `im:resource` 权限 |
