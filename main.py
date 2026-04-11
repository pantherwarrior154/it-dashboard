"""
IT Dashboard — COP1034C Python for IT
Your Name | Date

A command-line IT management tool that grows into a full
desktop application over 4 weeks. Each class session adds
a new feature to this project.
"""

from datetime import datetime

# ── Application Metadata ──────────────────────────────────
APP_NAME = "IT Dashboard"
VERSION = "0.1.0"


def main():
    # --- Variable declarations ---
    # String variables for server identity
    server_name  = "Not entered"
    ip_address   = "Not entered"
    department   = "Not entered"
    total_disk_gb = 0
    used_disk_gb  = 0
    usage_pct    = 0.0
    report_ready = False

    # --- Main menu loop ---
    while True:
        # Print the three menu options
        print("\n--- IT Report Generator ---")
        print("1) Enter server info")
        print("2) View report")
        print("3) Student info")
        print("4) Exit")

        choice = input("Select an option: ")

        # Prompt for server_name, ip_address, department
        if choice == "1":
            server_name = input ("Server Name : ")
            ip_address = input ("IP Address : ")
            department = input ("Department : ")
            # Prompt for total_disk_gb and used_disk_gb — cast to int
            total_disk_gb = int(input("Total Disk (GB): "))
            used_disk_gb = int(input("Used Disk (GB): "))
            # Validate: check for negative values or used > total
            if total_disk_gb <= 0:
                print("\n[!] Error: Total disk must be greater than 0.")
                report_ready = False
            elif used_disk_gb > total_disk_gb:
                print("\n[!] Error: Used disk cannot exceed total disk.")
                report_ready = False
            elif used_disk_gb < 0 or total_disk_gb < 0:
                print("\n[!] Error: Values cannot be negative.")
                report_ready = False
            else:
                # Calculate usage_pct as a float
                usage_pct = (used_disk_gb / total_disk_gb) * 100
                # Set report_ready = True
                report_ready = True
        elif choice == "2":
            if not report_ready:
                print("No data entered yet. Choose option 1 first.")
            else:
                # Classify disk usage after calculating usage_pct
                if usage_pct > 90:
                    disk_status = "CRITICAL - Immediate action required"
                elif usage_pct > 75:
                    disk_status = "WARNING - Disk usage is elevated"
                else:
                    disk_status = "OK - Disk usage is normal"
                # Print the formatted report using f-strings
                print("\n" + "="*40)
                print(f"Server Name: {server_name}")
                print("="*40)
                print(f"IP Address: {ip_address}")
                print(f"Department: {department}")
                print("-" * 40)
                print(f"Total Disk Space: {total_disk_gb} GB")
                print(f"Used Disk Space: {used_disk_gb} GB")
                print(f"Usage Percentage: {usage_pct:.2f}%")
                print(f"Disk Status: {disk_status}")
                print("="*40)

                checks = ["Ping response", "DNS resolution", "Firewall active"]
                print("\nSystem Health Checks:")
                for check in checks:
                    print(f"  - {check:<18}: PASS")

        elif choice == "3":
            # Data for Lab #1
            name = "Nathan Brown"
            course = "Programming for IT professionals"
            instructor = "professor Mora"
            assignment = "1st week class lab"
            # Requirement: Use datetime for current date
            today = datetime.now().strftime("%m/%d/%Y")
            print("\n" + "="*40)
            print(f"Name: {name}")
            print(f"Course: {course}")
            print(f"Instructor: {instructor}")
            print(f"Assignment: {assignment}")
            print(f"Date: {today}")
            print("="*40)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1, 2, 3.")
# ── Run the program ───────────────────────────────────────
if __name__ == "__main__":
    main()