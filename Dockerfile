FROM python:2.7
WORKDIR /SecureApp
ADD requirements.txt /SecureApp/
RUN pip install -r requirements.txt
ADD . /SecureApp
CMD python main.py
