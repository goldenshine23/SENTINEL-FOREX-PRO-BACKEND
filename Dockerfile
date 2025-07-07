# Use Windows-based Python image (needs Windows containers enabled)
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Python (modify as needed)
SHELL ["powershell", "-Command"]

RUN Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -OutFile python-installer.exe; \
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; \
    Remove-Item python-installer.exe -Force

WORKDIR /app

COPY requirements.txt .
RUN pip
 install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
