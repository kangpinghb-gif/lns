# Life Navigation System — Deployment Guide

> Version: 1.0 | Status: Frozen

## 1. Purpose

定义 LNS 系统部署流程与基础设施配置。

## 2. Architecture Overview

Docker Compose（开发/测试）→ Kubernetes（生产）→ CI/CD Pipeline

## 3. Infrastructure Components

- **PostgreSQL**：核心结构化数据
- **Redis**：状态缓存
- **Object Storage**：报告文件
- **Vector DB（V2）**：语义记忆

## 4. Deployment Steps

1. 环境变量配置
2. Database 初始化
3. Redis 启动
4. API Service 部署
5. Frontend 部署
6. AI Service 部署
7. Cron Job 配置（报告生成）

## 5. Environment Variables

| Variable | Description |
|---|---|
| `DB_URL` | PostgreSQL 连接地址 |
| `REDIS_URL` | Redis 连接地址 |
| `STORAGE_ENDPOINT` | 对象存储端点 |
| `LLM_API_KEY` | LLM API 密钥 |
| `LLM_MODEL` | LLM 模型名称 |
| `LOG_LEVEL` | 日志级别 |
| `RATE_LIMIT` | API 速率限制 |

## 6. Logging & Monitoring

- 结构化日志（JSON format）
- 请求追踪（trace_id）
- 性能指标（Engine 耗时）
- 错误报警
