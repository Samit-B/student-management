from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
import logging
from app.api.core.database.db import events_collection

logger = logging.getLogger(__name__)


router = APIRouter()

# ✅ Event Model
class Event(BaseModel):
    title: str
    date: str
    description: str

# ✅ Route to Add an Event
@router.post("/events/")
async def add_event(event: Event):
    event_dict = event.dict()
    result = events_collection.insert_one(event_dict)
    return {"message": "Event added successfully", "id": str(result.inserted_id)}

# ✅ Route to Get All Events
@router.get("/events/")
async def get_events():
    events = list(events_collection.find({}))
    for event in events:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string
    return {"events": events}

@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event by its ID
    
    Parameters:
    - event_id: The ID of the event to delete
    
    Returns:
    - Success message if deletion was successful
    """

    try:
        logger.info(f"Attempting to delete event with ID: {event_id}")
        if not event_id or not isinstance(event_id, str):
            logger.warning(f"Empty or invalid event ID type received: {type(event_id)}")

            raise HTTPException(
                status_code=400, 
                detail="Event ID is required and must be a string"
            )
            
        if not ObjectId.is_valid(event_id):
            logger.warning(f"Invalid event ID format received: {event_id}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid event ID format. Expected a 24-character hexadecimal string. Example: 507f1f77bcf86cd799439011"
            )


        logger.debug(f"Converting event_id to ObjectId: {event_id}")
        result = events_collection.delete_one({"_id": ObjectId(event_id)})
        logger.debug(f"Delete operation result: {result.raw_result}")

        if result.deleted_count == 0:
            logger.warning(f"Event not found for ID: {event_id}")
            logger.debug(f"Current events in collection: {list(events_collection.find({}))}")

            raise HTTPException(
                status_code=404, 
                detail=f"Event with ID {event_id} not found. Please verify the event ID and try again"
            )


        return {"message": f"Event {event_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while deleting event: {str(e)}"
        )
