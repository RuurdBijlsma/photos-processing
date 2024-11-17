from pydantic import BaseModel


class ProcessState(BaseModel):
    current_user: int = 0
    total_users: int = 1
    current_image: int = 0
    user_images: int = 1


process_state = ProcessState()
