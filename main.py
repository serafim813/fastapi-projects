from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from random import randint
import uuid
IMAGEDIR = "fastapi-images/"
from email_validator import validate_email, EmailNotValidError
import urlextract

from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    format_number,
    is_valid_number,
    number_type,
    parse as parse_phone_number,
)
from pydantic import BaseModel, constr, validator

MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE

class UserInfo(BaseModel):
    phone: constr(max_length=50, strip_whitespace=True)
    email: constr(max_length=63, strip_whitespace=True)
    comment: constr(max_length=63, strip_whitespace=True)
    pass

class Url(BaseModel):
    v: constr(max_length=50, strip_whitespace=True)
    pass

class UserInfo1(BaseModel):
    phone: constr(max_length=50, strip_whitespace=True)
    email: constr(max_length=63, strip_whitespace=True)
    comment: constr(max_length=63, strip_whitespace=True)

    @validator('phone')
    def check_phone_number(cls, v):
        if v is None:
            return v
        k = ''
        try:
            n = parse_phone_number(v, 'GB')
        except NumberParseException:
            k = 'Error phone message'
        if k == "Error phone message":
            return k
        elif not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            return "Error phone message"
        else:
            return format_number(n,  PhoneNumberFormat.INTERNATIONAL)

    @validator('email')
    def validate_email(cls, email):
        try:
            # Validate.
            valid = validate_email(email)

            # Update with the normalized form.
            a = valid.email
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            a = 'Error email message'
        return a

    @validator('comment')
    def validate_comment(cls, comment):
        extractor = urlextract.URLExtract()
        urls = extractor.find_urls(comment)
        return urls


app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return await request_validation_exception_handler(request, exc)

@app.post("/path/")
async def test(item: UserInfo):
    z = []
    item_dict = item.dict()
    print(item_dict)
    a = item_dict['phone']
    b = item_dict['email']
    c = item_dict['comment']
    l = {'a': a, 'b': b, 'c': c}
    a = UserInfo1.check_phone_number(l['a'])
    b = UserInfo1.validate_email(l['b'])
    c = UserInfo1.validate_comment(l['c'])
    if a == 'Error phone message':
        p = {'name': 'phone', 'error': "Error phone message"}
        z.append(p)
    if b == 'Error email message':
        p = {'name': 'email', 'error': "Error email message"}
        z.append(p)
    if len(c) != 0:
        p = {'name': 'comment', 'error': "Error comment message"}
        z.append(p)
    if len(z)!=0:
        raise HTTPException(status_code=422, detail = z)
    else:
        raise HTTPException(status_code=200, detail='Успешно!')
    return z

@app.post("/path/images/")
async def create_upload_file(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()  # <-- Important!

    # example of how you can save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    files = os.listdir(IMAGEDIR)
    path = f"{IMAGEDIR}{files[len(files)-1]}"
    
    return {"path": path}

@app.get('/image/')
async def read_random_file():
    #get a random file from the image directory
    files = os.listdir(IMAGEDIR)
    path =''
    if len(files) !=0:
        random_index = randint(0, len(files) - 1)
        path = f"{IMAGEDIR}{files[random_index]}"

    # notice you can use FileResponse now because it expects a path
    return {"path": path}

