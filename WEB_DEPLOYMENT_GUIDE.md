# AI Chat Guardian Web服务部署指南

## 📋 概述

AI Chat Guardian Web服务版提供了基于浏览器的用户界面和RESTful API，可以在局域网内部署，供团队成员共同使用。

## 🚀 快速启动

### Windows系统

1. **双击启动脚本**
   ```
   start_web.bat
   ```

2. **或使用命令行**
   ```bash
   python web_server.py --host 0.0.0.0 --port 5000
   ```

### Linux/Mac系统

```bash
chmod +x start_web.sh
./start_web.sh
```

## 🌐 访问方式

### 本机访问
```
http://localhost:5000
```

### 局域网访问
```
http://<服务器IP地址>:5000
```

**查看本机IP地址：**
- Windows: `ipconfig` (查看IPv4地址)
- Linux/Mac: `ifconfig` 或 `ip addr`

## 📡 API接口文档

### 1. 健康检查

**端点:** `GET /api/health`

**响应示例:**
```json
{
  "status": "healthy",
  "guardian_available": true,
  "llm_available": true,
  "llm_model": "gemma3:1b"
}
```

### 2. 文本检测

**端点:** `POST /api/detect`

**请求体:**
```json
{
  "text": "待检测的文本",
  "auto_obfuscate": true
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "has_sensitive": true,
    "detection_count": 2,
    "original_text": "公司营收5000万元",
    "safe_text": "公司营收[financial已隐藏]",
    "detections": [
      {
        "type": "financial",
        "content": "5000万元",
        "start": 4,
        "end": 11,
        "confidence": 0.8
      }
    ],
    "llm_raw_response": "..."
  }
}
```

### 3. 获取配置

**端点:** `GET /api/config`

**响应示例:**
```json
{
  "success": true,
  "config": {
    "llm_detector": {
      "enable": true,
      "model": "gemma3:1b",
      "threshold": 0.7
    }
  }
}
```

### 4. 获取可用模型

**端点:** `GET /api/models`

**响应示例:**
```json
{
  "success": true,
  "current_model": "gemma3:1b",
  "models": [
    {
      "name": "gemma3:1b",
      "description": "0.76GB - 最快,推荐日常使用"
    }
  ]
}
```

## ⚙️ 配置说明

### 自定义端口

```bash
python web_server.py --port 8080
```

### 仅本机访问（更安全）

```bash
python web_server.py --host 127.0.0.1 --port 5000
```

### 启用调试模式

```bash
python web_server.py --debug
```

## 🔒 安全建议

1. **防火墙配置**
   - 在生产环境中，请配置防火墙规则，仅允许信任的IP访问
   - Windows: 控制面板 → Windows Defender 防火墙 → 高级设置

2. **HTTPS支持**
   - 对于生产环境，建议使用Nginx或Apache作为反向代理
   - 配置SSL证书启用HTTPS加密传输

3. **访问控制**
   - 可以在代码中添加API密钥验证
   - 或使用Nginx的basic auth进行访问控制

## 🧪 测试服务

运行测试脚本验证服务是否正常：

```bash
python test_web_api.py
```

## 🐛 常见问题

### Q: 无法访问Web界面
**A:** 
1. 检查服务是否正常启动
2. 检查防火墙是否放行端口
3. 确认使用正确的IP地址

### Q: LLM检测器不可用
**A:** 
1. 确保Ollama服务已启动
2. 检查模型是否已下载
3. 查看配置文件中的模型名称是否正确

### Q: 检测速度慢
**A:** 
1. 使用更小的模型（如gemma3:1b）
2. 确保Ollama服务运行在本地
3. 检查系统资源占用情况

## 📊 性能优化

1. **模型选择**
   - 日常使用: gemma3:1b (0.76GB, 最快)
   - 高精度: qwen2.5:7b (4.36GB, 准确)

2. **并发处理**
   - Flask默认启用多线程
   - 可使用Gunicorn提高并发能力

3. **缓存策略**
   - 考虑对相同文本的检测结果进行缓存
   - 减少重复的LLM调用

## 📝 日志查看

服务运行日志会输出到控制台，包含：
- 请求信息
- 检测结果统计
- 错误信息
- 性能数据

## 🔄 更新部署

1. 拉取最新代码
2. 安装新依赖: `pip install -r requirements.txt`
3. 重启服务

## 📞 技术支持

- GitHub Issues: https://github.com/0qinghao/AI_chat_guardian/issues
- 文档: 查看项目README.md

---

**版本:** 1.0.0  
**更新日期:** 2025-10-24
