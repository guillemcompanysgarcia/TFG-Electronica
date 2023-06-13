#!/bin/sh 


if ! [ -x "$(command -v python3)" ]; then
  echo 'Error: Python3 is not installed.' >&2
  exit 1
fi

# Check if there is an internet connection
if ping -c 1 google.com &> /dev/null; then
  echo "Internet connection is up"
else
  echo "Internet connection is down"
  exit 1
fi



# Continuously run the Python script
while true; do
    # Navigate to the directory where your Python script is located
    cd "/home/proves/Desktop/Node XXXX/CP"
    # Run the Python script
    sudo python main.py
    # Check the exit status of the Python script
    if [ $? -ne 0 ]; then
        echo "Python script failed, restarting..."
    else
        break
    fi
done
