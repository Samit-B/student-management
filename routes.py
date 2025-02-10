from fastapi import APIRouter, Request, Form, HTTPException
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from database.db import collection

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ✅ Route to display all students
@router.get("/")
def get_students(request: Request):
    students = list(collection.find({}, {"_id": 1, "name": 1, "student_class": 1, "dob": 1, "gender": 1, "city": 1, "marks": 1}))
    for student in students:
        student["id"] = str(student["_id"])  # Convert ObjectId to string
    return templates.TemplateResponse("index.html", {"request": request, "students": students})

# ✅ Route to add a student
@router.post("/add/")
async def add_student(
    name: str = Form(...),
    student_class: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    marks: str = Form(...)
):
    student_data = {
        "name": name,
        "student_class": student_class,
        "dob": dob,
        "gender": gender,
        "city": city,
        "marks": marks
    }
    result = collection.insert_one(student_data)
    return {"message": "Student added successfully", "id": str(result.inserted_id)}

# ✅ Route to update a student
@router.post("/update/{student_id}")
async def update_student(
    student_id: str,
    name: str = Form(...),
    student_class: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    marks: int = Form(...),
):

    student_data = {
        "name": name,
        "student_class": student_class,
        "dob": dob,
        "gender": gender,
        "city": city,
        "marks": marks
    }

    result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student updated successfully"}

# ✅ Route to delete a student
@router.post("/delete/{student_id}")
async def delete_student(student_id: str):
    if not collection.find_one({"_id": ObjectId(student_id)}):
        raise HTTPException(status_code=404, detail="Student not found")

    collection.delete_one({"_id": ObjectId(student_id)})
    return {"message": "Student deleted successfully"}

@router.get("/students/marks")
async def get_student_marks():
    students = collection.find({}, {"name": 1, "marks": 1})  # Fetch only names and marks
    student_list = [{"name": student["name"], "marks": student.get("marks", 0)} for student in students]
    return student_list