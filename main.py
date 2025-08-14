
import requests
from datetime import datetime
import math 
import smtplib
import time

# Your coordinates (replace with your actual location)

MY_LAT = 20.593683 
MY_LONG = 78.962883 

# Email configuration - REPLACE WITH YOUR CREDENTIALS
my_mail = "your_email@gmail.com"  # Your Gmail address
password = "your_app_password_here"  # Your Gmail app password (not regular password)

def get_iss_position():
    """
    Fetches the current position of the ISS from the Open Notify API.
    Returns latitude and longitude as floats.
    """
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    
    return iss_latitude, iss_longitude

def is_night():
    """
    Determines if it's currently nighttime at the specified coordinates.
    Uses sunrise/sunset API to check if current time is between sunset and sunrise.
    
    Returns True if it's nighttime, False otherwise.
    """
    # Parameters for sunrise/sunset API
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,  # Returns time in UTC format
    }
    
    # Get sunrise and sunset times
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    
    # Extract hour from sunrise and sunset times (UTC)

    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    
    # Get current hour (local time)
    time_now = datetime.now().hour
    
    # Check if current time is between sunset and sunrise (nighttime)
    if time_now >= sunset or time_now <= sunrise:
        return True
    else:
        return False

def is_iss_overhead(iss_lat, iss_long):
    """
    Checks if the ISS is currently overhead (within 5 degrees of our position).
    
    Args:
        iss_lat: ISS latitude
        iss_long: ISS longitude
    
    Returns True if ISS is overhead, False otherwise.
    """

    if math.isclose(iss_lat, MY_LAT, abs_tol=5) and math.isclose(iss_long, MY_LONG, abs_tol=5):
        return True
    return False

def send_notification():
    """
    Sends an email notification that the ISS is overhead.
    Uses Gmail SMTP server to send the email.
    """
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()  
            connection.login(user=my_mail, password=password)
            connection.sendmail(
                from_addr=my_mail,
                to_addrs="fakerhere1803@gmail.com",  # Replace with recipient email
                msg="Subject: Look up in the sky!\n\nThe ISS is flying above you right now!"
            )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    """
    Main loop that continuously monitors the ISS position.
    Checks every 60 seconds if the ISS is overhead during nighttime.
    """
    print("ISS Overhead Notifier started...")
    print(f"Monitoring location: {MY_LAT}, {MY_LONG}")
    
    while True:
        try:
            # Get current ISS position
            iss_latitude, iss_longitude = get_iss_position()
            
            print(f"ISS Position: {iss_latitude}, {iss_longitude}")
            
            # Check if ISS is overhead AND it's nighttime
            if is_iss_overhead(iss_latitude, iss_longitude) and is_night():
                print("ISS is overhead and it's dark - sending notification!")
                send_notification()
                
                # Wait longer to avoid sending multiple emails for the same pass
                time.sleep(600)  # Wait 10 minutes before checking again
            else:
                print("ISS not overhead or it's daytime - waiting...")
                time.sleep(60)  
                
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()