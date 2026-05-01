#!/bin/bash
set -e

echo "Checking Microsoft ODBC Driver 18..."

if ! odbcinst -q -d -n "ODBC Driver 18 for SQL Server" >/dev/null 2>&1; then
    echo "ODBC Driver 18 not found. Installing..."

    apt-get update
    apt-get install -y curl gnupg apt-transport-https unixodbc unixodbc-dev

    . /etc/os-release

    if [ "$ID" = "debian" ]; then
        VERSION_ID_MAJOR=$(echo "$VERSION_ID" | cut -d. -f1)
        curl -sSL -O https://packages.microsoft.com/config/debian/$VERSION_ID_MAJOR/packages-microsoft-prod.deb
    elif [ "$ID" = "ubuntu" ]; then
        curl -sSL -O https://packages.microsoft.com/config/ubuntu/$VERSION_ID/packages-microsoft-prod.deb
    else
        echo "Unsupported Linux distribution: $ID $VERSION_ID"
        exit 1
    fi

    dpkg -i packages-microsoft-prod.deb
    rm packages-microsoft-prod.deb

    apt-get update
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

    echo "ODBC Driver 18 installed."
else
    echo "ODBC Driver 18 already installed."
fi

echo "Installed ODBC drivers:"
odbcinst -q -d

echo "Starting Flask API with gunicorn..."
gunicorn --bind=0.0.0.0:${PORT:-8000} run:app