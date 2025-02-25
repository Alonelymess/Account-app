from fastapi import FastAPI 
from utils.handle import DataHandle

app = FastAPI()

data = DataHandle()

@app.get("/")
async def read():
    return data.read

@app.post("/append")
async def append(item):
    data.append(item)
    
@app.delete("/delete/{index}")
async def delete(index):
    data.delete(index)

@app.put("/update/{index}")
async def update(index, item):
    data.update(index, item)