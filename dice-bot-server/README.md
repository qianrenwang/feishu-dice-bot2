# 🎲 飞书骰子机器人部署指南

这是一个可以部署到群聊的飞书骰子机器人，支持多种骰子类型（D6、D10、D20、D100）。

## 📋 支持的指令

| 指令 | 说明 | 示例 |
|------|------|------|
| 甩个六面骰 / D6 | 1-6 骰子 | @机器人 甩个六面骰 |
| D10 / 十面骰 | 1-10 骰子 | @机器人 D10 |
| D20 / 二十面骰 | 1-20 骰子 | @机器人 D20 |
| D100 / 百面骰 | 1-100 骰子 | @机器人 D100 |
| 1-50 | 自定义范围 | @机器人 1-50 |

---

## 🚀 部署方案对比

| 方案 | 成本 | 难度 | 适合场景 |
|------|------|------|----------|
| **Vercel** | 免费 | ⭐⭐ | 长期稳定使用 |
| **阿里云函数** | 免费额度 | ⭐⭐⭐ | 国内访问快 |
| **腾讯云函数** | 免费额度 | ⭐⭐⭐ | 国内访问快 |
| **本地+ngrok** | 免费 | ⭐ | 快速测试 |

---

## 方案一：Vercel 部署（推荐）

### 优点
- ✅ 完全免费
- ✅ 无需服务器
- ✅ 自动 HTTPS
- ✅ 全球 CDN 加速

### 步骤

1. **注册 Vercel 账号**
   - 访问 https://vercel.com
   - 用 GitHub 账号登录

2. **创建 GitHub 仓库**
   - 新建一个仓库，如 `feishu-dice-bot`
   - 将 `vercel/` 文件夹内的文件上传到仓库

3. **部署到 Vercel**
   - 在 Vercel Dashboard 点击 "Add New Project"
   - 选择你的 GitHub 仓库
   - Framework Preset 选择 "Other"
   - 点击 Deploy

4. **获取 Webhook URL**
   - 部署成功后，Vercel 会给你一个域名
   - Webhook URL 为：`https://你的域名.vercel.app/api/index`

5. **配置飞书**
   - 进入飞书开放平台 → 你的应用 → 事件与回调
   - 填写 Webhook URL
   - 订阅事件：`im.message.receive_v1`

---

## 方案二：本地 + ngrok 快速测试

### 优点
- ✅ 立即可用，无需注册
- ✅ 适合测试功能

### 缺点
- ❌ ngrok 免费版 URL 每次重启会变
- ❌ 电脑关机后服务停止

### 步骤

1. **安装依赖**
```bash
cd local-ngrok
pip install -r requirements.txt
```

2. **启动本地服务**
```bash
python app.py
```
服务会在 `http://localhost:5000` 启动

3. **安装 ngrok**
   - 访问 https://ngrok.com 注册账号
   - 下载 ngrok 客户端
   - 复制 authtoken

4. **启动 ngrok 隧道**
```bash
ngrok config add-authtoken 你的token
ngrok http 5000
```

5. **获取 Webhook URL**
   - ngrok 会显示一个公网 URL，如 `https://xxxx.ngrok-free.app`
   - Webhook URL 为：`https://xxxx.ngrok-free.app/webhook`

6. **配置飞书**
   - 将 Webhook URL 填入飞书开放平台

---

## 方案三：阿里云函数计算

### 优点
- ✅ 每月免费 100 万次调用
- ✅ 国内访问速度快

### 步骤

1. **登录阿里云控制台**
   - 访问 https://fc.console.aliyun.com

2. **创建服务和函数**
   - 创建服务：`dice-bot-service`
   - 创建函数：选择 "HTTP 函数"
   - 运行环境：Python 3.9
   - 将 `aliyun-fc/index.py` 代码粘贴进去

3. **获取 HTTP 触发器地址**
   - 函数创建后会自动生成 HTTP 触发器 URL

4. **配置飞书**
   - 将 HTTP 触发器 URL 填入飞书开放平台

---

## 🔧 飞书后台配置

### 1. 开通权限
进入飞书开放平台 → 你的应用 → 权限管理，开通：
- `im:message:send_as_bot` - 以机器人身份发送消息
- `im:message:receive_v1` - 接收用户消息
- `im:chat:readonly` - 读取群组信息

### 2. 配置事件订阅
进入「事件与回调」：
- 选择 "Webhook" 模式
- 填写你的 Webhook URL
- 添加订阅事件：`im.message.receive_v1`

### 3. 发布应用
- 点击「版本管理与发布」
- 创建版本，填写更新说明
- 申请发布（需管理员审核）

### 4. 邀请机器人入群
- 在群聊设置 → 群机器人 → 添加机器人
- 找到你的应用并添加

---

## 🧪 测试

部署完成后，在群里艾特机器人：
```
@骰子助手 甩个六面骰
@骰子助手 D20
@骰子助手 1-100
```

机器人会回复精美的卡片消息，显示骰子结果！

---

## ❓ 常见问题

**Q: 机器人不回复？**
- 检查 Webhook URL 是否正确
- 检查权限是否已开通
- 检查应用是否已发布
- 检查是否在群内添加了机器人

**Q: ngrok URL 失效？**
- 免费版 ngrok URL 每次重启会变
- 需要重新配置飞书的 Webhook URL
- 或升级到付费版获取固定域名

**Q: 如何生成真实的骰子图片？**
- 当前版本使用飞书卡片消息
- 如需真实骰子图片，需要接入图片生成服务
- 可以联系我升级版本

---

## 📞 技术支持

如有问题，请联系开发者或使用本地测试版本先验证功能。

祝你玩得开心！🎲