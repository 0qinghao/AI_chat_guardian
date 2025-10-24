# 🚀 AI Chat Guardian 快速开始指南

## 5分钟快速启动Web服务

### 第一步：确保Ollama服务运行

```powershell
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 如果未运行，启动Ollama
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
```

### 第二步：启动Web服务

**方式1: 双击启动脚本（推荐）**
```
双击: start_web.bat
```

**方式2: 命令行启动**
```powershell
python web_server.py
```

### 第三步：访问Web界面

在浏览器中打开：
```
http://localhost:5000
```

### 第四步：开始使用

1. **输入文本** - 在左侧输入框粘贴或输入待检测的文本
2. **点击检测** - 点击"🔍 检测并混淆"按钮
3. **查看结果** - 右侧显示混淆后的安全文本，下方显示详细检测信息

---

## 局域网访问设置

### 1. 查看本机IP地址

```powershell
ipconfig
```

找到"IPv4 地址"，例如：`192.168.1.100`

### 2. 配置防火墙（首次需要）

**Windows防火墙：**
1. 控制面板 → Windows Defender 防火墙 → 高级设置
2. 入站规则 → 新建规则
3. 端口 → TCP → 特定本地端口 → 5000
4. 允许连接 → 完成

**或使用命令（管理员权限）：**
```powershell
netsh advfirewall firewall add rule name="AI Guardian Web" dir=in action=allow protocol=TCP localport=5000
```

### 3. 局域网设备访问

在同一局域网的其他设备浏览器中输入：
```
http://192.168.1.100:5000
```

（将IP替换为你的实际IP地址）

---

## API调用示例

### Python调用

```python
import requests

# 检测文本
response = requests.post(
    'http://localhost:5000/api/detect',
    json={
        'text': '公司Q3营收5000万元，API密钥sk-123456',
        'auto_obfuscate': True
    }
)

result = response.json()
if result['success']:
    data = result['data']
    print(f"检测到 {data['detection_count']} 处敏感信息")
    print(f"混淆后: {data['safe_text']}")
```

### JavaScript调用

```javascript
// 检测文本
fetch('http://localhost:5000/api/detect', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        text: '公司Q3营收5000万元',
        auto_obfuscate: true
    })
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        console.log('检测结果:', data.data);
    }
});
```

### curl调用

```bash
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d '{"text":"公司Q3营收5000万元","auto_obfuscate":true}'
```

---

## 常见问题

### Q1: 服务启动失败？
**A:** 检查端口5000是否被占用
```powershell
netstat -ano | findstr :5000
```

### Q2: LLM检测器不可用？
**A:** 确保：
1. Ollama服务已启动
2. 模型已下载（`ollama pull gemma3:1b`）
3. 配置文件中的模型名称正确

### Q3: 检测速度慢？
**A:** 
1. 切换到更小的模型（gemma3:1b）
2. 检查系统资源占用
3. 确保Ollama服务在本地运行

### Q4: 无法从其他设备访问？
**A:** 
1. 确认启动时使用了 `--host 0.0.0.0`
2. 检查防火墙设置
3. 确认设备在同一局域网

---

## 进阶配置

### 自定义端口

```powershell
python web_server.py --port 8080
```

### 仅本机访问（更安全）

```powershell
python web_server.py --host 127.0.0.1
```

### 启用调试模式

```powershell
python web_server.py --debug
```

---

## 测试服务

运行测试脚本：

```powershell
python test_web_api.py
```

---

## 获取帮助

- 📖 详细文档: `WEB_DEPLOYMENT_GUIDE.md`
- 🏆 参赛文档: `AI_COMPETITION_PROPOSAL.md`
- 🐛 问题反馈: https://github.com/0qinghao/AI_chat_guardian/issues

---

**快速启动完成！开始体验AI守护者的强大功能吧！** 🎉
