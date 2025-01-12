from fastapi import APIRouter, Form, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import os, shutil, base64
from .models import ResidentModel, AddRequest, GetRequest
from traceback import format_exc

import random, string, json
from apps.voice import similarity

import time  # Ensure this is imported at the top of your server file
from datetime import datetime
'''
UTILS
'''

def gen_id():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return random_string
router = APIRouter()


# Allowed time window in seconds (e.g., 60 seconds)
ALLOWED_TIME_WINDOW = 60

def is_valid_timestamp(timestamp: float) -> bool:
    current_time = time.time()
    return abs(current_time - timestamp) <= ALLOWED_TIME_WINDOW

'''
ROUTERS
'''
@router.post("/add", response_description="Add new resident")
async def add_resident(request: Request, payload: AddRequest):
    if not payload.payload:
        raise HTTPException(status_code=400, detail="No payload provided.")

    try:
        # Decrypt the payload using Caesar cipher
        decrypted_json_str = caesar_decrypt(payload.payload)
        print(f"Decrypted JSON Payload: {decrypted_json_str}")

        # Parse the decrypted JSON
        decrypted_doc = json.loads(decrypted_json_str)

        # Validate timestamp
        if 'timestamp' not in decrypted_doc:
            raise HTTPException(status_code=400, detail="Timestamp missing in payload.")
        
        timestamp = decrypted_doc['timestamp']
        if not is_valid_timestamp(timestamp):
            raise HTTPException(status_code=400, detail="Invalid or expired timestamp.")

        # Extract other fields
        name = decrypted_doc.get('name')
        file_base64 = decrypted_doc.get('file')

        if not file_base64:
            raise HTTPException(status_code=400, detail="File data missing in payload.")

        # Decode Base64 file and save it
        temp_id = gen_id()
        file_path = f"./tmp/{temp_id}"
        os.makedirs(file_path, exist_ok=True)
        wav_file_path = os.path.join(file_path, "uploaded_file.wav")
        
        file_data = base64.b64decode(file_base64.encode("utf-8"))
        with open(wav_file_path, "wb") as f:
            f.write(file_data)

        # (Rest of your existing processing logic)
        model = request.app.state.voice
        result = model.process(wav_file_path)
        command = result.get("text", None)
        voice = result.get("spk", None)

        print("COMMAND: ", command)

        if voice is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={'request': "POST", "detail": "Cannot recognize speaker."}
            )

        resident_data = ResidentModel(name=name, voice=voice, id=temp_id)
        db = request.app.mongodb["iot"]
        new_resident = db.insert_one(resident_data.dict(by_alias=True))

        # Encrypt the response if needed (optional)
        response_content = json.dumps({'request': "POST", "_id": str(new_resident.inserted_id)}).encode('utf-8')
        encrypted_response = caesar_encrypt(response_content.decode('utf-8'))  # Implement caesar_encrypt on server if needed

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'response': encrypted_response}
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")
    except Exception as e:
        print(format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
@router.post("/get", response_description="Get open/shut command")
async def get_command(request: Request, payload: GetRequest):
    if not payload.payload:
        raise HTTPException(status_code=400, detail="No payload provided.")

    try:
        # Decrypt the payload using Caesar cipher
        decrypted_json_str = caesar_decrypt(payload.payload)
        print(f"Decrypted JSON Payload: {decrypted_json_str}")

        # Parse the decrypted JSON
        decrypted_doc = json.loads(decrypted_json_str)

        # Validate timestamp
        if 'timestamp' not in decrypted_doc:
            raise HTTPException(status_code=400, detail="Timestamp missing in payload.")
        
        timestamp = decrypted_doc['timestamp']
        if not is_valid_timestamp(timestamp):
            raise HTTPException(status_code=400, detail="Invalid or expired timestamp.")

        # Extract file
        file_base64 = decrypted_doc.get('file')

        if not file_base64:
            raise HTTPException(status_code=400, detail="File data missing in payload.")

        # Decode Base64 file and save it
        temp_id = gen_id()
        file_path = f"./tmp/{temp_id}"
        os.makedirs(file_path, exist_ok=True)
        wav_file_path = os.path.join(file_path, "uploaded_file.wav")
        
        file_data = base64.b64decode(file_base64.encode("utf-8"))
        with open(wav_file_path, "wb") as f:
            f.write(file_data)

        # (Rest of your existing processing logic)
        model = request.app.state.voice
        result = model.process(wav_file_path)
        command = result.get("text", None)
        voice = result.get("spk", None)

        print("COMMAND: ", command)

        # Check for a matching speaker
        mx = 0
        mx_spk = None
        if voice is not None: 
            for speaker in request.app.mongodb["iot"].find().to_list(length=100):
                sim = similarity(voice, speaker["voice"])
                if mx < sim:
                    mx = sim
                    mx_spk = speaker["name"]
                print(speaker["name"], sim)

        # Prepare the response
        response_dict = {
            "request": "POST",
            "action": 1 if mx > 0.8 else 0,
            "command": command,
            "name": mx_spk if mx > 0.8 else "guest"
        }

        # Encrypt the response if needed (optional)
        response_content = json.dumps(response_dict).encode('utf-8')
        encrypted_response = caesar_encrypt(response_content.decode('utf-8'))  # Implement caesar_encrypt on server if needed

        # Prepare final response
        final_response = {
            'response': encrypted_response
        }

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=final_response
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")
    except Exception as e:
        print(format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/list", response_description="List all id")
async def get(request: Request):
    try:    
        result = []
        for speaker in request.app.mongodb["iot"].find().to_list(length=100):
            result.append({"_id": speaker["_id"], "name": speaker["name"]})

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content=result
        )
    except Exception as e:
        print(format_exc())
        raise HTTPException(status_code=500, detail=f"Error list ids: {str(e)}")
    
@router.get("/logs", response_description="List all log")
async def get(request: Request):
    try:    
        result = []
        for speaker in request.app.mongodb["history"].find().to_list(length=100):
            result.append({"id": speaker["id"], "name": speaker["name"], "time": speaker["inTime"]})
        # print(result)
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content=result
        )
    except Exception as e:
        print(format_exc())
        raise HTTPException(status_code=500, detail=f"Error list ids: {str(e)}")

@router.delete("/delete/{id}", response_description="Delete resident")
async def delete(id: str, request: Request):
    delete_result = request.app.mongodb["iot"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"request": "DELETE", "_id": id})

    raise HTTPException(status_code=404, detail=f"Resident {id} not found")

@router.delete("/delete_log/{id}", response_description="Delete log")
async def delete(id: str, request: Request):
    delete_result = request.app.mongodb["history"].delete_one({"id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"request": "DELETE", "id": id})

    raise HTTPException(status_code=404, detail=f"Logs {id} not found")