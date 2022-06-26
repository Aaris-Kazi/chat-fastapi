from fastapi import Depends, FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List
from requests import request
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
import models
from database import SessionLocal, engine
import uvicorn

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    async def broadcast(self, message: str):
        print(message)
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get('/')
def read_temp(request: Request,db: Session = Depends(get_db)):
    # try:
    #     add = models.Users(name = 'Admin', password = 'admin')
    #     db.add(add)
    #     db.commit()
    #     return "success"
    # except Exception as e:
    #     return "Issue occured "+e
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/chat')
def read_temp(request: Request,db: Session= Depends(get_db),  username: str = Form(), password: str = Form()):
    if request.method == 'POST':
        print(username)
        print(password)
        sel = select(models.Users).where(and_(models.Users.name == username, models.Users.password == password))
        res = engine.execute(sel).fetchone()
        
        print(res)
        if not res:
            print('Failed')
            return templates.TemplateResponse('index.html', {"request": request})
        else:
            print('success')
            return templates.TemplateResponse('chat.html', {"request": request, 'uname': username})
    
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/room')
def read_temp(request: Request,db: Session= Depends(get_db),  username: str = Form(), password: str = Form()):
    if request.method == 'POST':
        print(username)
        print(password)
        sel = select(models.Users).where(and_(models.Users.name == username, models.Users.password == password))
        res = engine.execute(sel).fetchone()
        
        print(res)
        if not res:
            print('Failed')
            return templates.TemplateResponse('index.html', {"request": request})
        else:
            print('success')
            return templates.TemplateResponse('room.html', {"request": request, 'uname': username})
    
    return templates.TemplateResponse('index.html', {"request": request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id : str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"{client_id}You wrote: {data}", websocket)
            
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect as w:
        print(w)
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
        
        
        
if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1")
    uvicorn.run(app)

# uvicorn main:app --reload
# web: gunicorn -w 3 -k uvicorn.workers.UvicornWorker