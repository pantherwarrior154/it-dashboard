"""
IT Dashboard — COP1034C Python for IT
Your Name | Date

A command-line IT management tool that grows into a full
desktop application over 4 weeks. Each class session adds
a new feature to this project.
"""

from datetime import datetime
import turtle

# ── ANSI Color Codes ─────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

SEVERITY_COLORS = {
    "ERROR":    RED,
    "CRITICAL": RED,
    "WARNING":  YELLOW,
    "INFO":     GREEN,
}

# ── Network Device Classes ────────────────────────────────

class NetworkDevice:
    """Base class representing a generic network device.

    Attributes:
        hostname    (str)  : device hostname, e.g. CORE-RTR-01
        ip_address  (str)  : IPv4 address, e.g. 10.0.0.1
        device_type (str)  : 'router', 'switch', etc.
        status      (str)  : 'online' or 'offline'
    """

    def __init__(self, hostname, ip_address, device_type, status="online"):
        """Initialize a NetworkDevice with identity and status fields."""
        self.hostname    = hostname
        self.ip_address  = ip_address
        self.device_type = device_type
        self.status      = status

    def __str__(self):
        """Return a one-line summary string for this device."""
        return f"[{self.device_type}] {self.hostname} | {self.ip_address} | Status: {self.status}"

    def ping(self):
        """Simulate a ping to this device and return a result string."""
        return f"Reply from {self.ip_address}: bytes=32 time=2ms TTL=64"

    def get_info(self):
        """Return a formatted string with this device's details."""
        return (f"Hostname : {self.hostname}\n"
                f"IP       : {self.ip_address}\n"
                f"Type     : {self.device_type}\n"
                f"Status   : {self.status}")

    def set_status(self, new_status):
        """Update the device status to the given string."""
        self.status = new_status


class Router(NetworkDevice):
    """A network router. Extends NetworkDevice with routing information.

    Additional Attributes:
        routing_protocol (str)  : e.g. 'OSPF', 'BGP', 'EIGRP', 'Static'
        routes           (list) : list of route strings in CIDR notation
    """

    def __init__(self, hostname, ip_address, routing_protocol="OSPF"):
        """Initialize a Router — calls super().__init__ with device_type='router'."""
        super().__init__(hostname, ip_address, device_type="router")
        self.routing_protocol = routing_protocol
        self.routes = []

    def get_info(self):
        """Override base get_info to include routing protocol and routes."""
        routes_str = ", ".join(self.routes) if self.routes else "None"
        return (f"{str(self)}\n"
                f"  Protocol : {self.routing_protocol}\n"
                f"  Routes   : {routes_str}")

    def show_routes(self):
        """Return a list of routes this router knows about."""
        if not self.routes:
            return ["10.0.0.0/8", "192.168.0.0/24", "0.0.0.0/0"]
        return self.routes

    def add_route(self, route):
        """Add a route string to this router's route list."""
        self.routes.append(route)


class Switch(NetworkDevice):
    """A network switch. Extends NetworkDevice with VLAN and port information.

    Additional Attributes:
        port_count (int)  : number of switchports (e.g. 24 or 48)
        vlans      (list) : list of VLAN description strings
    """

    def __init__(self, hostname, ip_address, port_count=24):
        """Initialize a Switch — calls super().__init__ with device_type='switch'."""
        super().__init__(hostname, ip_address, device_type="switch")
        self.port_count = port_count
        self.vlans = ["VLAN 1 (default)"]

    def get_info(self):
        """Override base get_info to include port count and VLAN list."""
        vlans_str = ", ".join(self.vlans)
        return (f"{str(self)}\n"
                f"  Ports    : {self.port_count}\n"
                f"  VLANs    : {vlans_str}")

    def show_vlans(self):
        """Return the current list of VLAN description strings."""
        return self.vlans

    def add_vlan(self, vlan_description):
        """Add a VLAN description string to this switch's VLAN list."""
        self.vlans.append(vlan_description)


class DeviceManager:
    """Manages a collection of NetworkDevice objects.

    Provides add, remove, find, and list operations over
    the internal devices list.
    """

    def __init__(self):
        """Initialize with an empty device list."""
        self.devices = []

    def add_device(self, device):
        """Add a NetworkDevice (or subclass) to the devices list."""
        self.devices.append(device)
        print(f"[+] Added {device.hostname} to manager.")

    def remove_device(self, hostname):
        """Remove the device with the given hostname. Print a message if not found."""
        for device in self.devices:
            if device.hostname == hostname:
                self.devices.remove(device)
                print(f"[-] Removed {hostname} from manager.")
                return
        print(f"[!] Device '{hostname}' not found.")

    def find_device(self, hostname):
        """Return the device object matching hostname, or None if not found."""
        for device in self.devices:
            if device.hostname == hostname:
                return device
        return None

    def list_all(self):
        """Print the get_info() output for every device in the list."""
        if not self.devices:
            print("No devices in manager.")
            return
        print("\n--- Network Devices ---")
        for device in self.devices:
            # Color the device type label by type
            color = GREEN if device.device_type == "router" else CYAN
            print(f"{color}{device.get_info()}{RESET}")
            print("-" * 40)

    def uptime_percentage(self):
        """Return the percentage of devices currently marked online."""
        if not self.devices:
            return 0.0
        online = sum(1 for d in self.devices if d.status == "online")
        return (online / len(self.devices)) * 100

    def avg_response_time(self):
        """Return a simulated average ping response time in ms.

        Uses the last octet of each device's IP to vary the value.
        """
        if not self.devices:
            return 0.0
        times = []
        for d in self.devices:
            try:
                # Simulate response time from last octet of IP
                last_octet = int(d.ip_address.split(".")[-1])
                times.append(1 + (last_octet % 10))
            except (ValueError, IndexError):
                times.append(2)
        return sum(times) / len(times)

    def devices_per_subnet(self):
        """Return a dict mapping each /24 subnet to a count of devices on it."""
        subnets = {}
        for d in self.devices:
            try:
                # Build the /24 subnet string from the first three octets
                parts = d.ip_address.split(".")
                subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            except IndexError:
                subnet = "unknown"
            subnets[subnet] = subnets.get(subnet, 0) + 1
        return subnets


# ── Application Metadata ──────────────────────────────────
APP_NAME = "IT Dashboard"
VERSION  = "0.1.0"


def draw_topology(manager):
    """Draw a simple network topology using turtle.

    Each device is drawn as a rectangle with its hostname
    labeled below it. Devices are spaced evenly across the screen.
    """
    if not manager.devices:
        print("No devices to draw.")
        return

    screen = turtle.Screen()
    screen.title("Network Topology")
    screen.bgcolor("#0a0e1a")

    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()

    x_start = -200
    x_step  =  150
    y_pos   =    0

    for i, device in enumerate(manager.devices):
        x = x_start + (i * x_step)

        t.penup()
        t.goto(x, y_pos)
        t.pendown()

        if device.device_type == "router":
            t.fillcolor("#10b981")
        else:
            t.fillcolor("#3b82f6")

        t.color("white")
        t.begin_fill()
        for _ in range(2):
            t.forward(60)
            t.left(90)
            t.forward(40)
            t.left(90)
        t.end_fill()

        t.penup()
        t.goto(x + 30, y_pos - 20)
        t.color("white")
        t.write(device.hostname, align="center", font=("Arial", 9, "normal"))

    turtle.done()


# ── Network Manager Menu Functions ───────────────────────

def show_menu():
    """Print the network manager sub-menu options."""
    print("\n--- Network Device Manager ---")
    print("  a) Add device")
    print("  r) Remove device")
    print("  l) List all devices")
    print("  p) Ping a device")
    print("  s) Show statistics")
    print("  d) Draw topology")
    print("  b) Back to main menu")


def handle_add(manager):
    """Prompt the user for device details and add a new device to the manager."""
    print("\nDevice type: (1) Router  (2) Switch")
    dtype = input("Select type: ").strip()
    hostname   = input("Hostname   : ").strip()
    ip_address = input("IP Address : ").strip()

    if dtype == "1":
        # Router — ask for routing protocol
        protocol = input("Routing Protocol (OSPF/BGP/EIGRP/Static) [OSPF]: ").strip() or "OSPF"
        device = Router(hostname, ip_address, routing_protocol=protocol)
    elif dtype == "2":
        # Switch — ask for port count
        try:
            ports = int(input("Port count [24]: ").strip() or "24")
        except ValueError:
            ports = 24
        device = Switch(hostname, ip_address, port_count=ports)
    else:
        print("[!] Invalid type selection.")
        return

    manager.add_device(device)


def handle_remove(manager):
    """Prompt for a hostname and remove that device from the manager."""
    hostname = input("Hostname to remove: ").strip()
    manager.remove_device(hostname)


def handle_ping(manager):
    """Prompt for a hostname and display a simulated ping result."""
    hostname = input("Hostname to ping: ").strip()
    device = manager.find_device(hostname)
    if device:
        print(device.ping())
    else:
        print(f"[!] Device '{hostname}' not found.")


def run_network_manager():
    """Run the network device manager sub-menu loop."""
    manager = DeviceManager()
    while True:
        show_menu()
        choice = input("Select an option: ").strip().lower()
        if choice == "a":
            handle_add(manager)
        elif choice == "r":
            handle_remove(manager)
        elif choice == "l":
            manager.list_all()
        elif choice == "p":
            handle_ping(manager)
        elif choice == "s":
            print(f"\n--- Device Statistics ---")
            print(f"  Uptime        : {manager.uptime_percentage():.1f}%")
            print(f"  Avg Response  : {manager.avg_response_time():.1f} ms")
            print(f"  Devices/Subnet:")
            for subnet, count in manager.devices_per_subnet().items():
                print(f"    {subnet:<20}: {count} device(s)")
        elif choice == "d":
            draw_topology(manager)
        elif choice == "b":
            break
        else:
            print("Invalid choice.")


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
        print("5) Network Device Manager")
        print("6) Exit")

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
            run_network_manager()
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1-6.")
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
    print(f"Total errors found: {SEVERITY_COLORS['ERROR']}{len(error_entries)}{RESET}")
    print(f"Summary written to log_summary.txt")
    print(f"  {SEVERITY_COLORS['ERROR']}Unique ERROR messages: {len(unique_errors)}{RESET}")
    print(f"  {RED}Critical events:       {len(critical_events)}{RESET}")


# ── Run the program ───────────────────────────────────────
if __name__ == "__main__":
    main()