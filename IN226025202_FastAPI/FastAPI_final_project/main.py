from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
import math

app = FastAPI()

# -------------------- MODELS --------------------

class EnrollmentRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=5)
    email: str = Field(..., min_length=5)
    payment_type: str = "online"


class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    seats_left: int = Field(..., gt=0)


class CheckoutRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)

# -------------------- DATA --------------------

courses = [{"id": 1, "title": "HTML & CSS", "instructor": "John", "category": "Web Dev", "level": "Beginner", "price": 999, "seats_left": 20},
    {"id": 2, "title": "JavaScript Basics", "instructor": "Alice", "category": "Web Dev", "level": "Beginner", "price": 1499, "seats_left": 15},
    {"id": 3, "title": "React JS", "instructor": "David", "category": "Web Dev", "level": "Intermediate", "price": 2999, "seats_left": 10},
    {"id": 4, "title": "Node.js Backend", "instructor": "Emma", "category": "Web Dev", "level": "Advanced", "price": 3499, "seats_left": 8},
    {"id": 5, "title": "Full Stack Web Dev", "instructor": "Sophia", "category": "Web Dev", "level": "Advanced", "price": 4999, "seats_left": 5},
    {"id": 6, "title": "Python for Data Science", "instructor": "Mike", "category": "Data Science", "level": "Beginner", "price": 1999, "seats_left": 18},
    {"id": 7, "title": "Machine Learning", "instructor": "Chris", "category": "Data Science", "level": "Intermediate", "price": 3999, "seats_left": 12},
    {"id": 8, "title": "Deep Learning", "instructor": "Olivia", "category": "Data Science", "level": "Advanced", "price": 4499, "seats_left": 7},
    {"id": 9, "title": "Data Analysis with Pandas", "instructor": "Liam", "category": "Data Science", "level": "Intermediate", "price": 2799, "seats_left": 14},
    {"id": 10, "title": "Statistics for Data Science", "instructor": "Noah", "category": "Data Science", "level": "Beginner", "price": 1599, "seats_left": 20},
    {"id": 11, "title": "UI Design Fundamentals", "instructor": "Ava", "category": "Design", "level": "Beginner", "price": 1999, "seats_left": 16},
    {"id": 12, "title": "UX Research", "instructor": "James", "category": "Design", "level": "Intermediate", "price": 2499, "seats_left": 12},
    {"id": 13, "title": "Figma Masterclass", "instructor": "Lucas", "category": "Design", "level": "Intermediate", "price": 2299, "seats_left": 10},
    {"id": 14, "title": "Graphic Design Pro", "instructor": "Mason", "category": "Design", "level": "Advanced", "price": 3199, "seats_left": 6},
    {"id": 15, "title": "Motion Graphics", "instructor": "Isabella", "category": "Design", "level": "Advanced", "price": 3499, "seats_left": 5},
    {"id": 16, "title": "AWS Cloud Basics", "instructor": "Benjamin", "category": "DevOps", "level": "Beginner", "price": 2999, "seats_left": 18},
    {"id": 17, "title": "Docker Essentials", "instructor": "Charlotte", "category": "DevOps", "level": "Intermediate", "price": 2799, "seats_left": 14},
    {"id": 18, "title": "Kubernetes", "instructor": "Henry", "category": "DevOps", "level": "Advanced", "price": 3999, "seats_left": 9},
    {"id": 19, "title": "CI/CD Pipelines", "instructor": "Daniel", "category": "DevOps", "level": "Intermediate", "price": 2599, "seats_left": 11},
    {"id": 20, "title": "Terraform Basics", "instructor": "Grace", "category": "DevOps", "level": "Beginner", "price": 2399, "seats_left": 17}
]

enrollments = []
enrollment_counter = 1
cart = []

# -------------------- HELPERS --------------------

def find_course(course_id):
    for course in courses:
        if course["id"] == course_id:
            return course
    return None

def calculate_price(price, seats):
    return price * seats

def filter_courses_logic(category=None, level=None, max_price=None):
    filtered = []
    for course in courses:
        if category is not None and course["category"] != category:
            continue
        if level is not None and course["level"] != level:
            continue
        if max_price is not None and course["price"] > max_price:
            continue
        filtered.append(course)
    return filtered

# -------------------- ROUTES --------------------

@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Course Platform"}

@app.get("/courses")
def get_courses():
    return {
        "courses": courses,
        "total": len(courses),
        "total_seats_available": sum(c["seats_left"] for c in courses)
    }

@app.get("/courses/summary")
def summary():
    category_count = {}
    level_count = {}

    for c in courses:
        category_count[c["category"]] = category_count.get(c["category"], 0) + 1
        level_count[c["level"]] = level_count.get(c["level"], 0) + 1

    return {
        "total_courses": len(courses),
        "total_seats_available": sum(c["seats_left"] for c in courses),
        "courses_per_category": category_count,
        "courses_per_level": level_count
    }

@app.get("/courses/search")
def search(keyword: str = Query(...)):
    result = [
        c for c in courses
        if keyword.lower() in c["title"].lower()
        or keyword.lower() in c["category"].lower()
    ]
    if not result:
        return {"message": "No courses found"}
    return {"results": result, "total_found": len(result)}

@app.get("/courses/filter")
def filter_courses(category: str = None, level: str = None, max_price: int = None):
    result = filter_courses_logic(category, level, max_price)
    return {"filtered_courses": result, "count": len(result)}

@app.get("/courses/sort")
def sort_courses(sort_by="price", order="asc"):
    if sort_by not in ["price", "title", "category"]:
        raise HTTPException(400, "Invalid sort_by")
    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    return {
        "courses": sorted(courses, key=lambda x: x[sort_by], reverse=(order == "desc"))
    }

@app.get("/courses/page")
def paginate(page: int = Query(1, ge=1), limit: int = Query(5, ge=1, le=10)):
    start = (page - 1) * limit
    return {
        "courses": courses[start:start+limit],
        "total_pages": math.ceil(len(courses) / limit)
    }

@app.get("/courses/browse")
def browse(keyword: str = None, sort_by="price", order="asc", page=1, limit=5):
    data = courses.copy()

    if keyword:
        data = [
            c for c in data
            if keyword.lower() in c["title"].lower()
            or keyword.lower() in c["category"].lower()
        ]

    if sort_by not in ["price", "title", "category"]:
        raise HTTPException(400, "Invalid sort_by")

    data = sorted(data, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    return {"courses": data[start:start+limit]}

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

# -------------------- ENROLL --------------------

@app.post("/enroll")
def enroll(req: EnrollmentRequest):
    global enrollment_counter

    course = find_course(req.course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    if course["seats_left"] < req.seats:
        raise HTTPException(400, "Not enough seats")

    total = calculate_price(course["price"], req.seats)

    discount = 0
    if req.payment_type == "offline":
        discount = round(total * 0.1, 2)
        total -= discount

    enrollment = {
        "id": enrollment_counter,
        "student": req.student_name,
        "course": course["title"],
        "payment_type": req.payment_type,
        "discount": discount,
        "total_price": total
    }

    enrollments.append(enrollment)
    course["seats_left"] -= req.seats
    enrollment_counter += 1

    return enrollment

# -------------------- ENROLLMENT OPS --------------------

@app.get("/enrollments")
def get_enrollments():
    return {"enrollments": enrollments}

@app.get("/enrollments/search")
def search_enrollments(name: str):
    return [e for e in enrollments if name.lower() in e["student"].lower()]

@app.get("/enrollments/sort")
def sort_enrollments(order="asc"):
    return sorted(enrollments, key=lambda x: x["total_price"], reverse=(order=="desc"))

# -------------------- CRUD --------------------

@app.post("/courses")
def add_course(course: NewCourse):
    if any(c["title"].lower() == course.title.lower() for c in courses):
        raise HTTPException(400, "Duplicate course")

    new = course.dict()
    new["id"] = len(courses) + 1
    courses.append(new)
    return new

@app.put("/courses/{course_id}")
def update(course_id: int, price: int = None, seats_left: int = None):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    if price is not None:
        course["price"] = price
    if seats_left is not None:
        course["seats_left"] = seats_left

    return course

@app.delete("/courses/{course_id}")
def delete(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    courses.remove(course)
    return {"message": "Deleted"}

# -------------------- CART --------------------

@app.post("/cart/add")
def add_cart(course_id: int, seats: int = 1):
    course = find_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    cart.append({"course_id": course_id, "seats": seats})
    return cart

@app.get("/cart")
def view_cart():
    return cart

@app.delete("/cart/{course_id}")
def remove(course_id: int):
    for item in cart:
        if item["course_id"] == course_id:
            cart.remove(item)
            return {"message": "Removed"}
    raise HTTPException(404, "Not found")

@app.post("/cart/checkout")
def checkout(req: CheckoutRequest):
    global enrollment_counter

    if not cart:
        raise HTTPException(400, "Cart empty")

    result = []
    for item in cart:
        result.append({"id": enrollment_counter})
        enrollment_counter += 1

    cart.clear()
    return result