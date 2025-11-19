# AI Chat Guardian - Web版使用指南

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install flask flask-cors
```

### 2. 启动服务

**Windows:**
```bash
start_web.bat
```

**Linux/Mac:**
```bash
chmod +x start_web.sh
./start_web.sh
```

### 3. 访问系统
- **本地**: http://localhost:5000
- **内网**: http://你的IP地址:5000

## 📖 使用说明

1. **输入文本**: 在文本框中输入要检测的内容
2. **点击检测**: 点击"检测并混淆"按钮
3. **查看结果**: 
   - 左侧显示混淆后的安全文本
   - 右侧显示检测到的敏感信息详情
4. **复制使用**: 点击"复制"按钮将安全文本复制到剪贴板

## 🔧 配置

编辑 `config/default_config.yaml` 修改检测配置:

```yaml
detection:
  enable_regex: true      # 正则表达式检测
  enable_keyword: true    # 关键词检测  
  enable_llm: true        # LLM检测

llm_detector:
  model: gemma3:1b        # LLM模型
  threshold: 0.7          # 检测阈值
```

## 📱 内网访问设置

### 获取本机IP

**Windows:**
```bash
ipconfig
```
找到"IPv4 地址"

**Linux/Mac:**
```bash
ifconfig
# 或
ip addr show
```

### 配置防火墙

**Windows防火墙:**
```bash
netsh advfirewall firewall add rule name="AI Guardian" dir=in action=allow protocol=TCP localport=5000
```

**Linux (firewalld):**
```bash
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

### 同事访问

告诉同事在浏览器中访问:
```
http://你的IP地址:5000
```

例如: `http://192.168.1.100:5000`

## 🧪 测试

运行测试脚本验证服务:
```bash
python test_web_api.py
```

## 📚 完整文档

详细的部署和配置文档请查看: [docs/WEB_DEPLOYMENT.md](docs/WEB_DEPLOYMENT.md)

## ⚙️ 高级配置

### 修改端口
如果5000端口被占用:

**临时修改:**
```bash
set FLASK_PORT=8080    # Windows
export FLASK_PORT=8080  # Linux/Mac
```

**永久修改:**
编辑 `web/app.py` 第183行:
```python
port = int(os.environ.get('FLASK_PORT', 8080))
```

### 后台运行

**Linux (nohup):**
```bash
cd web
nohup python3 app.py > ../logs/web.log 2>&1 &
```

**Windows (后台任务):**
```bash
start /B python web\app.py
```

### 生产部署

使用Gunicorn (推荐):
```bash
pip install gunicorn
cd web
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 常见问题

### 访问不了页面?
1. 检查服务是否启动 (查看终端输出)
2. 检查防火墙设置
3. 确认IP地址正确
4. 尝试先访问 http://localhost:5000

### LLM检测不工作?
1. 确认Ollama已启动: `ollama serve`
2. 确认模型已下载: `ollama list`
3. 检查配置文件: `config/default_config.yaml`

### 检测速度慢?
1. 使用更小的模型 (gemma3:1b)
2. 关闭不需要的检测器
3. 增加服务器性能

## 📞 支持

- **文档**: `docs/WEB_DEPLOYMENT.md`
- **日志**: `logs/web.log`
- **测试**: `python test_web_api.py`

---

**版本**: Web 1.0  
**更新**: 2025年10月24日
