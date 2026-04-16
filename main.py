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
        print("4) Analyze server log")
        print("5) Exit")

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
            analyze_log()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1-5.")
def analyze_log():
    """Reads server.log, parses entries, and writes log_summary.txt."""
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path     = os.path.join(script_dir, 'server.log')
    summary_path = os.path.join(script_dir, 'log_summary.txt')
    # Severity counter — keys added dynamically using .get() to avoid KeyError
    severity_counts = {}
    # Set for unique ERROR messages — add() ignores duplicates
    unique_errors = set()
    # Set for unique CRITICAL events
    critical_events = set()
    # List of all parsed entries as dicts
    log_entries = []

    # Requirement 9: Wrap file open in try/except for clean error handling
    try:
        # Requirement 1: open and iterate line by line
        with open(log_path, 'r') as f:
            for line in f:
                # Requirement 2: strip() removes trailing whitespace/newlines
                line = line.strip()
                if not line:
                    continue

                # Requirement 2: split with maxsplit=3 keeps message intact
                parts = line.split(maxsplit=3)
                if len(parts) < 4:
                    continue

                # Requirement 3: slicing for date (chars 0-10)
                date_field = line[:10]

                time_field = parts[1]

                # Requirement 2: strip("[]") removes brackets, upper() normalizes case
                severity = parts[2].strip("[]").upper()

                message = parts[3]

                # Requirement 4: increment count using .get() with default 0
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

                # Requirement 5: track unique ERROR messages
                if severity == "ERROR":
                    unique_errors.add(message)

                # Track unique CRITICAL events
                if severity == "CRITICAL":
                    critical_events.add(message)

                # Requirement 6: append parsed entry to list
                log_entries.append({'date': date_field, 'time': time_field, 'severity': severity, 'message': message})

    except FileNotFoundError:
        print("Error: server.log not found. Place the log file in the same directory as this script.")
        exit(1)

    # Requirement 10: list comprehension for ERROR entries only
    error_entries = [e for e in log_entries if e["severity"] == "ERROR"]

    error_rate = (len(error_entries) / len(log_entries) * 100) if log_entries else 0

    # Requirement 7: write summary report
    with open(summary_path, 'w') as out:
        print("=" * 36, file=out)
        print(f"{'SERVER LOG ANALYSIS REPORT':^36}", file=out)
        print("=" * 36, file=out)
        # Requirement 8: f-string with field-width format spec for alignment
        print(f"{'Log File':<12}: server.log", file=out)
        print(f"{'Lines Read':<12}: {len(log_entries)}", file=out)
        print("-" * 36, file=out)
        print("SEVERITY COUNTS", file=out)
        for level in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            count = severity_counts.get(level, 0)
            print(f"  {level:<10}: {count:>2}", file=out)
        print("-" * 36, file=out)
        print(f"ERROR RATE  : {error_rate:.2f}%", file=out)
        print("-" * 36, file=out)
        print(f"UNIQUE ERRORS ({len(unique_errors)} total)", file=out)
        for msg in sorted(unique_errors):
            print(f"  - {msg}", file=out)
        print(f"CRITICAL EVENTS ({len(critical_events)} total)", file=out)
        for msg in sorted(critical_events):
            print(f"  - {msg}", file=out)
        print("=" * 36, file=out)

    print(f"\nLog analysis complete. {len(log_entries)} entries processed.")
    print(f"Total errors found: {len(error_entries)}")
    print(f"Summary written to log_summary.txt")
    print(f"  Unique ERROR messages: {len(unique_errors)}")
    print(f"  Critical events:       {len(critical_events)}")


# ── Run the program ───────────────────────────────────────
if __name__ == "__main__":
    main()