import csv
import random

NUM_RECORDS = 1000

users = {
    1: {
        "primary_ip": "120.45",
        "secondary_ip": "121.45",
        "hour_range": (9, 18),
        "rare_hour": (22, 23),
        "main_device": "Desktop"
    },
    2: {
        "primary_ip": "150.20",
        "secondary_ip": "151.20",
        "hour_range": (18, 23),
        "rare_hour": (8, 10),
        "main_device": "Mobile"
    },
    3: {
        "primary_ip": "175.60",
        "secondary_ip": "176.60",
        "hour_range": (8, 22),
        "rare_hour": (1, 3),
        "main_device": "Desktop"
    }
}

with open("login_dataset.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "user_id",
        "login_hour",
        "ip_group",
        "device_type"
    ])

    for _ in range(NUM_RECORDS):
        user_id = random.choice(list(users.keys()))
        user = users[user_id]

        # 85% normal hour
        if random.random() < 0.85:
            login_hour = random.randint(*user["hour_range"])
        else:
            login_hour = random.randint(*user["rare_hour"])

        # 80% primary IP
        if random.random() < 0.8:
            ip_group = user["primary_ip"]
        else:
            ip_group = user["secondary_ip"]

        # 85% main device
        if random.random() < 0.85:
            device_type = user["main_device"]
        else:
            device_type = "Mobile" if user["main_device"] == "Desktop" else "Desktop"

        writer.writerow([
            user_id,
            login_hour,
            ip_group,
            device_type
        ])

print("Realistic synthetic dataset generated.")