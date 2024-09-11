from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.core.database import get_db, engine
from src import models
from src.routers import personal, employee, role,leave,admin
from src.core.authentication import router as auth_router, authenticate_employee, create_access_token
from pathlib import Path
from fastapi.responses import HTMLResponse
from src.core.authentication import *
from src.core.authentication import oauth2_scheme,get_current_user_function
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json
from chatcode.function import *
from chatcode.api_call import *
from chatcode.onbfunction import collect_user_input, validate_input,get_jsonfile
import asyncio

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/templates", StaticFiles(directory=Path(__file__).resolve().parent / "templates"), name="templates")


app.include_router(personal.router)
app.include_router(employee.router)
app.include_router(role.router)
app.include_router(leave.router)
app.include_router(admin.router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def get():
    file_path = Path(__file__).resolve().parent / "templates" / "index.html"
    if not file_path.exists():
        return HTMLResponse("File not found", status_code=404)
    return HTMLResponse(file_path.read_text())

@app.get("/profile")
async def get_profile(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    db_user =  get_current_user_function(db, token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authenticated"
        )
    return db_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.websocket("/ws/onboard")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            user_message = data_json.get("message", "").strip().lower()            
            print(f"Received message: '{user_message}'")  # Debugging: Log the received message

            if user_message == 'quit':
                await websocket.send_text("Please wait,You will be Navigated to Login Screen")  # Redirect to the new page
                await asyncio.sleep(3)  # Add a 3-second delay
                await websocket.send_text("navigate")  # Redirect to the new page
                break

            elif user_message == 'onboard':
                file = get_jsonfile()
                details = await collect_user_input(websocket, file, validate_input)
                details['dateofbirth'] = datetime.strptime(details['dateofbirth'], '%Y-%m-%d').strftime('%Y-%m-%d')
                details['contactnumber'] = int(details['contactnumber'])
                print('*****************************')
                print(details)
                print('*****************************')
                response = await onboard_personal_details(websocket,details)
                print(response)
                if response != "Email Send Successfully":
                    await websocket.send_text(response)
                    await websocket.send_text("You will be Navigated to Login Screen")  # Redirect to the new page
                    await asyncio.sleep(7)  # Add a 3-second delay
                    await websocket.send_text("navigate")
                    break
                else:
                    await websocket.send_text("Your details have been saved successfully. Check your personal mail for Username and Password.")
                    await websocket.send_text("You will be Navigated to Login Screen")  # Redirect to the new page
                    await asyncio.sleep(7)  # Add a 3-second delay
                    await websocket.send_text("navigate")
                    break
            else:
                await websocket.send_text("Please enter 'Onboard' in the chat below or 'Quit' to exit.")
    
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Exception: {e}")
        await websocket.send_text(json.dumps({"Response": "An error occurred. Please try again."}))


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # Receiving data
                data = await websocket.receive_text()
                data_json = json.loads(data)
                print('________________________________________________________________________________________')
                print("data_json", data_json)
                print('________________________________________________________________________________________')

                token = data_json.get("token")
                user_message = data_json.get("message")
                role = data_json.get("role")

                # Check for 'quit' message
                if user_message.lower() == 'quit':
                    await websocket.send_text("Goodbye, Thanks for using our app!")
                    break
                
                # Main logic
                jsonfile = choose_json(role)
                query, project_name = await get_project_details(websocket, user_message, jsonfile)
                project_details = get_project_script(project_name, jsonfile)
                payload_details = split_payload_fields(project_details)
                
                filled_cleaned = await fill_payload_values(websocket, query, payload_details, jsonfile)
                validate_payload = validate(project_details, filled_cleaned)
                
                # Handling PUT requests
                if validate_payload['method'] == 'PUT':
                    answer = await update_process(websocket, project_details, validate_payload)
                    print("---------------------------------------------------------------------------------------------------------------------------")
                    logger.info(f"Answer from update_process: {answer}")
                    print("---------------------------------------------------------------------------------------------------------------------------")
                else:
                    # Handling other requests
                    answer = await ask_user(websocket, project_details, validate_payload)
                    print("---------------------------------------------------------------------------------------------------------------------------")
                    logger.info(f"Answer from ask_user: {answer}")
                    print("---------------------------------------------------------------------------------------------------------------------------")
                
                answer['bearer_token'] = token
                
                # Database operation
                result = await database_operation(websocket, answer)
                
                if not result:
                    await websocket.send_text("Thanks for using. Need anything, feel free to ask!")
                else:
                    # Processing the result
                    model_output = nlp_response(result)
                    await websocket.send_text(model_output + " Thanks for using. Need anything, feel free to ask!")
            
            except json.JSONDecodeError:
                await websocket.send_text("Invalid input format. Please send a valid JSON.")
            except KeyError as e:
                await websocket.send_text(f"Missing required field: {str(e)}")
            except Exception as e:
                # Catch-all for unexpected errors
                await websocket.send_text(f"An error occurred: {str(e)}")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket connection: {str(e)}")
    finally:
        await websocket.close()


