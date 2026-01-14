# AssetHub 资产管理系统

## 目录结构

- `backend/` FastAPI 服务
- `frontend/` Vue 3 前端
- `docker-compose.yml` 一键启动

## 本地启动

后端:

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端:

```bash
cd frontend
npm install
npm run dev
```

初始化系统账号:

```bash
curl -X POST http://localhost:8000/api/v1/auth/init
```

默认管理员账号: `admin` / `admin123`。

## Docker 启动

```bash
docker compose up --build
```

前端访问: http://localhost:8080
后端 API: http://localhost:8000
