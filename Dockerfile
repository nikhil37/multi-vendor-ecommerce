FROM ubuntu
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt update -y
RUN apt install -y python3 python3-pip
RUN pip install -r requirements.txt
COPY . /code/
CMD ["python3","/code/manage.py","runserver","0.0.0.0:8000"]