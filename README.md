# Hunter-Search
一个使用鹰图API 进行信息资产收集的AI MCP-Server 的本地服务器 ，用于网络安全人员进行AI辅助

## api获取：

登录鹰图

[鹰图平台(hunter)-奇安信网络空间测绘系统](https://hunter.qianxin.com/)

![](docs/1.png)

## 设置：

在 config/settings.yaml 里填写你的 api-key

## 安装运行：

在使用之前以确保安装了python。

```bash
git clone https://github.com/nmwzsrgl2/Hunter-Search.git
cd Hunter-Search 
python -m venv myenv 
./.myenv/Scripts/activate   #linux: source ./.myenv/bin/activate 
pip install -r requirements.txt
python mcp_server.py
```

## 使用说明：

这里以 trae 为例子：

在 设置 --> mcp 导入：

```
{
  "mcpServers": {
    "huntu_search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

