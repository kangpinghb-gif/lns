# Life Navigation System — Security & Compliance

> Version: 1.0 | Status: Frozen

## 1. Purpose
定义 LNS 系统的安全架构与合规要求。

## 2. User Privacy
- 出生信息属于敏感数据
- 用户数据不可跨账号访问
- 用户有权删除所有个人数据

## 3. Data Encryption
- 传输层：TLS 1.3
- 存储层：AES-256 加密
- 敏感字段：birth_date, birth_time, birth_place 必须加密存储

## 4. API 签名
所有 API 请求必须携带签名：{api_key, timestamp, signature, nonce}

## 5. Rate Limiting
Free: 20 req/min, Pro: 200 req/min, Enterprise: unlimited

## 6. 审计日志
必须记录：用户操作、Engine 调用、决策输出、异常行为。日志保留至少90天。

## 7. Compliance
预留：GDPR（欧洲）、PDPA（亚太）、个人信息保护法（中国）合规接口。

## 8. Content Safety
禁止输出：医疗建议、法律结论、命运预测、恐吓性内容、歧视性内容。
