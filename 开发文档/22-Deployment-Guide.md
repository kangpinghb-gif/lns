# Life Navigation System — Deployment Guide

> Version: 1.1 | Status: Current Test Deployment

## 1. Purpose

定义 LNS 系统部署流程与基础设施配置。

## 2. Architecture Overview

当前阶段采用：

```text
Docker Compose（本机测试）→ 云端测试环境（待定）→ 生产环境（待定）
```

当前项目还没有 PostgreSQL、Redis、对象存储的实际接入代码。测试环境优先使用容器内 SQLite，避免过早引入复杂基础设施。

## 3. Infrastructure Components

当前测试环境：

- **API Service**：Python HTTPServer
- **Frontend**：`LNS/static/` 静态页面，由同一 Python 服务提供
- **Database**：SQLite，容器卷 `lns_test_data`

后续生产规划：

- **PostgreSQL**：核心结构化数据
- **Redis**：状态缓存
- **Object Storage**：报告文件
- **Vector DB（V2）**：语义记忆

## 4. Local Test Deployment

### 4.1 Docker Compose

在 `LNS/` 目录执行：

```bash
docker compose -f docker-compose.test.yml up --build
```

访问：

```text
http://127.0.0.1:8080/
http://127.0.0.1:8080/static/create.html
http://127.0.0.1:8080/static/kline.html
```

健康检查：

```bash
curl http://127.0.0.1:8080/health
```

停止：

```bash
docker compose -f docker-compose.test.yml down
```

清空测试数据：

```bash
docker compose -f docker-compose.test.yml down -v
```

### 4.2 Local Python Fallback

当本机没有 Docker Desktop 时，使用本地 Python 测试服务：

```bash
cd /Users/kangping/Developer/bookshelf/人生导航/lns-docs/LNS
bash scripts/run_local_test.sh
```

默认端口为 `8080`。如需改端口：

```bash
PORT=8090 bash scripts/run_local_test.sh
```

本地 Python fallback 会使用 `LNS/db/data/lns.db`，因此会写入当前工作区的 SQLite 测试数据；Docker Compose 方式则使用容器卷 `lns_test_data`。

## 5. Deployment Steps

1. 构建 Docker 镜像
2. 启动 `lns-test` 服务
3. 打开 `create.html`
4. 完成 `create -> kline -> year-detail` 主流程验证
5. 检查 `/health`
6. 测试完成后按需保留或清空 `lns_test_data`

## 6. Environment Variables

| Variable | Description |
|---|---|
| `LOG_LEVEL` | 日志级别 |
| `LLM_API_KEY` | LLM API 密钥，可选 |
| `LLM_MODEL` | LLM 模型名称，可选 |

生产规划变量，当前测试容器不依赖：

| Variable | Description |
|---|---|
| `DB_URL` | PostgreSQL 连接地址，生产规划 |
| `REDIS_URL` | Redis 连接地址，生产规划 |
| `STORAGE_ENDPOINT` | 对象存储端点，生产规划 |
| `RATE_LIMIT` | API 速率限制 |

## 7. Logging & Monitoring

- 结构化日志（JSON format）
- 请求追踪（trace_id）
- 性能指标（Engine 耗时）
- 错误报警

当前测试环境先使用容器标准输出日志。后续上云后再接入集中日志和告警。
