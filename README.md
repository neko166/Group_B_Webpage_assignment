# Group_B_Webpage_assignment

groupBのWebページ制作の課題です

## 開発環境構築コマンド

```bash
py -3.13 -m venv .venv
(PS)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process; .\.venv\Scripts\Activate.ps1
(cmd)
.\.venv\Scripts\Activate.bat
```

```bash
(venv)
python.exe -m pip install --upgrade pip
pip install python-dotenv
pip install fastapi sqlalchemy
pip install "fastapi[all]" jinja2
pip install bcrypt
pip install "PyJWT[crypto]"
pip install python-multipart
pip install httpx
```

### 起動

```bash
cloudflared tunnel --url http://localhost:8000
```
```bash
cd src
uvicorn main:app --reload --port 8000
```
