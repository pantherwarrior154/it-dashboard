# Final Project — IT Dashboard
# Description: A command-line IT utility tool with three features:
#   (1) A log analyzer that reads server.log line by line, counts severity
#       levels, tracks unique errors, and writes a formatted summary report.
#   (2) A network device manager that stores Router and Switch objects,
#       supports add/remove/search/ping operations, and draws a turtle topology.
#   (3) A password strength checker that evaluates passwords against length,
#       complexity, and common-password rules; accepts a single password or
#       reads multiple passwords from a file.
# Author: Nathan Brown
# Date: April 27, 2026

from datetime import datetime
import os
import platform
import re
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
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
    if dtype not in ("1", "2"):
        print("[!] Invalid type selection.")
        return

    hostname   = input("Hostname   : ").strip()
    ip_address = input("IP Address : ").strip()

    # Validate that neither field is blank
    if not hostname or not ip_address:
        print("[!] Hostname and IP address cannot be blank.")
        return

    if dtype == "1":
        # Router — ask for routing protocol
        protocol = input("Routing Protocol (OSPF/BGP/EIGRP/Static) [OSPF]: ").strip() or "OSPF"
        device = Router(hostname, ip_address, routing_protocol=protocol)
    else:
        # Switch — ask for port count
        try:
            ports = int(input("Port count [24]: ").strip() or "24")
        except ValueError:
            ports = 24
        device = Switch(hostname, ip_address, port_count=ports)

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


# ── Password Strength Checker ─────────────────────────────

def load_common_passwords():
    """Load common passwords from common_passwords.txt into a set.

    Returns an empty set if the file is not found so the checker
    still works without the file.
    """
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common_passwords.txt")
    try:
        with open(path, "r") as f:
            # Strip whitespace and lowercase each line; ignore blank lines
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def check_password_strength(password, common_passwords):
    """Evaluate a password and return a (score, feedback) tuple.

    Rules checked:
      - Length >= 8
      - Contains uppercase letter
      - Contains lowercase letter
      - Contains a digit
      - Contains a special character
      - Not in the common passwords list
    Score 0-6 maps to: Weak (0-2), Fair (3-4), Strong (5-6).
    """
    feedback = []
    score = 0

    # Rule 1: length
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Too short — use at least 8 characters")

    # Rule 2: uppercase
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter")

    # Rule 3: lowercase
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter")

    # Rule 4: digit
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add at least one number")

    # Rule 5: special character
    special = set("!@#$%^&*()-_=+[]{}|;:',.<>?/`~")
    if any(c in special for c in password):
        score += 1
    else:
        feedback.append("Add at least one special character (!@#$%...)")

    # Rule 6: not a common password
    if password.lower() not in common_passwords:
        score += 1
    else:
        feedback.append("This is a commonly used password — choose another")

    # Determine rating label
    if score <= 2:
        rating = f"{RED}Weak{RESET}"
    elif score <= 4:
        rating = f"{YELLOW}Fair{RESET}"
    else:
        rating = f"{GREEN}Strong{RESET}"

    return score, rating, feedback


def run_password_checker():
    """Run the password strength checker — accepts single input or a file of passwords."""
    common_passwords = load_common_passwords()

    print("\n--- Password Strength Checker ---")
    print("  1) Check a single password")
    print("  2) Check passwords from a file")
    mode = input("Select mode: ").strip()

    if mode == "1":
        # Single password check
        password = input("Enter password: ").strip()
        if not password:
            print("[!] No password entered.")
            return
        score, rating, feedback = check_password_strength(password, common_passwords)
        print(f"\n  Score  : {score}/6")
        print(f"  Rating : {rating}")
        if feedback:
            print("  Tips   :")
            for tip in feedback:
                print(f"    - {tip}")

    elif mode == "2":
        # Read passwords from a file
        filepath = input("Enter file path: ").strip()
        try:
            with open(filepath, "r") as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] File not found: {filepath}")
            return

        print(f"\n{'Password':<20} {'Score':>5}  Rating")
        print("-" * 40)
        for pw in passwords:
            score, rating, _ = check_password_strength(pw, common_passwords)
            # Mask all but first 2 chars for display
            masked = pw[:2] + "*" * (len(pw) - 2)
            print(f"  {masked:<18} {score:>5}/6  {rating}")
    else:
        print("[!] Invalid selection.")


def strip_ansi(text):
    """Remove ANSI escape sequences from text for GUI display."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class ITDashboardGUI:
    """Simple Tkinter front-end for key IT Dashboard features."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IT Dashboard")
        self.root.geometry("880x620")
        self.root.minsize(760, 560)
        # Keep rendering crisp on high-DPI displays.
        self.root.tk.call("tk", "scaling", 1.0)
        self.style = ttk.Style(self.root)
        self.current_theme = "neon"
        self.refresh_interval_seconds = 30
        self.countdown_seconds = self.refresh_interval_seconds
        self.refresh_job = None
        self.countdown_job = None

        self.common_passwords = load_common_passwords()
        self._build_ui()
        self.apply_theme()
        self.refresh_my_info()
        self.start_system_info_auto_refresh()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_theme_colors(self):
        """Return the neon palette used by all tabs and controls."""
        return {
            "bg": "#020409",
            "surface": "#070d17",
            "surface_alt": "#0d1728",
            "fg": "#d9fbff",
            "muted": "#61ddff",
            "accent": "#00e5ff",
            "input_bg": "#01050f",
            "input_fg": "#eaffff",
        }

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12, style="Dashboard.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="Dashboard.TFrame")
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="IT Dashboard",
            style="DashboardTitle.TLabel",
        ).pack(side="left")

        self.theme_label = ttk.Label(
            header,
            text="Theme: Neon",
            style="DashboardMeta.TLabel",
        )
        self.theme_label.pack(side="right")

        self.notebook = ttk.Notebook(container, style="Dashboard.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        system_tab = ttk.Frame(self.notebook, style="Dashboard.TFrame", padding=10)
        my_info_tab = ttk.Frame(self.notebook, style="Dashboard.TFrame", padding=10)
        server_tab = ttk.Frame(self.notebook, style="Dashboard.TFrame", padding=10)
        tools_tab = ttk.Frame(self.notebook, style="Dashboard.TFrame", padding=10)
        output_tab = ttk.Frame(self.notebook, style="Dashboard.TFrame", padding=10)

        self.notebook.add(system_tab, text="System Info")
        self.notebook.add(my_info_tab, text="My Info")
        self.notebook.add(server_tab, text="Server")
        self.notebook.add(tools_tab, text="Tools")
        self.notebook.add(output_tab, text="Output")

        system_frame = ttk.LabelFrame(system_tab, text="Live System Status", padding=10, style="Dashboard.TLabelframe")
        system_frame.pack(fill="x")

        self.system_last_refresh_var = tk.StringVar(value="Last refresh: --")
        self.system_countdown_var = tk.StringVar(value=f"Next refresh in: {self.refresh_interval_seconds}s")
        self.system_platform_var = tk.StringVar(value="Platform: --")
        self.system_python_var = tk.StringVar(value="Python: --")
        self.system_cwd_var = tk.StringVar(value="Working directory: --")
        self.system_cpu_var = tk.StringVar(value="CPU cores: --")

        ttk.Label(system_frame, textvariable=self.system_last_refresh_var, style="Dashboard.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Label(system_frame, textvariable=self.system_countdown_var, style="Dashboard.TLabel").grid(
            row=0, column=3, sticky="e", padx=6, pady=4
        )
        ttk.Label(system_frame, textvariable=self.system_platform_var, style="Dashboard.TLabel").grid(
            row=1, column=0, columnspan=4, sticky="w", padx=6, pady=4
        )
        ttk.Label(system_frame, textvariable=self.system_python_var, style="Dashboard.TLabel").grid(
            row=2, column=0, columnspan=4, sticky="w", padx=6, pady=4
        )
        ttk.Label(system_frame, textvariable=self.system_cwd_var, style="Dashboard.TLabel").grid(
            row=3, column=0, columnspan=4, sticky="w", padx=6, pady=4
        )
        ttk.Label(system_frame, textvariable=self.system_cpu_var, style="Dashboard.TLabel").grid(
            row=4, column=0, columnspan=4, sticky="w", padx=6, pady=4
        )
        ttk.Button(
            system_frame,
            text="Refresh Now",
            style="Dashboard.TButton",
            command=self.refresh_system_info,
        ).grid(row=5, column=0, padx=6, pady=(8, 2), sticky="w")

        my_info_frame = ttk.LabelFrame(my_info_tab, text="Student Info", padding=10, style="Dashboard.TLabelframe")
        my_info_frame.pack(fill="x")

        self.info_name_var = tk.StringVar(value="Name: Nathan Brown")
        self.info_course_var = tk.StringVar(value="Course: Programming for IT professionals")
        self.info_instructor_var = tk.StringVar(value="Instructor: professor Mora")
        self.info_assignment_var = tk.StringVar(value="Assignment: 1st week class lab")
        self.info_date_var = tk.StringVar(value="Date: --")

        ttk.Label(my_info_frame, textvariable=self.info_name_var, style="Dashboard.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Label(my_info_frame, textvariable=self.info_course_var, style="Dashboard.TLabel").grid(
            row=1, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Label(my_info_frame, textvariable=self.info_instructor_var, style="Dashboard.TLabel").grid(
            row=2, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Label(my_info_frame, textvariable=self.info_assignment_var, style="Dashboard.TLabel").grid(
            row=3, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Label(my_info_frame, textvariable=self.info_date_var, style="Dashboard.TLabel").grid(
            row=4, column=0, columnspan=3, sticky="w", padx=6, pady=4
        )
        ttk.Button(
            my_info_frame,
            text="Refresh Date",
            style="Dashboard.TButton",
            command=self.refresh_my_info,
        ).grid(row=5, column=0, padx=6, pady=(8, 2), sticky="w")

        server_frame = ttk.LabelFrame(server_tab, text="Server Report", padding=10, style="Dashboard.TLabelframe")
        server_frame.pack(fill="x")

        self.server_name_var = tk.StringVar()
        self.ip_address_var = tk.StringVar()
        self.department_var = tk.StringVar()
        self.total_disk_var = tk.StringVar()
        self.used_disk_var = tk.StringVar()

        self._add_labeled_entry(server_frame, "Server Name", self.server_name_var, 0, 0)
        self._add_labeled_entry(server_frame, "IP Address", self.ip_address_var, 0, 2)
        self._add_labeled_entry(server_frame, "Department", self.department_var, 1, 0)
        self._add_labeled_entry(server_frame, "Total Disk (GB)", self.total_disk_var, 1, 2)
        self._add_labeled_entry(server_frame, "Used Disk (GB)", self.used_disk_var, 2, 0)

        ttk.Button(server_frame, text="Generate Report", style="Dashboard.TButton", command=self.generate_server_report).grid(
            row=2, column=2, padx=6, pady=6, sticky="ew"
        )

        tools_frame = ttk.LabelFrame(tools_tab, text="Quick Tools", padding=10, style="Dashboard.TLabelframe")
        tools_frame.pack(fill="x")

        ttk.Button(tools_frame, text="Analyze Server Log", style="Dashboard.TButton", command=self.run_log_analysis).grid(
            row=0, column=0, padx=6, pady=6, sticky="ew"
        )

        self.password_var = tk.StringVar()
        self._add_labeled_entry(tools_frame, "Password", self.password_var, 0, 1)
        ttk.Button(tools_frame, text="Check Password", style="Dashboard.TButton", command=self.check_password).grid(
            row=0, column=3, padx=6, pady=6, sticky="ew"
        )

        ttk.Button(tools_frame, text="Open Network Manager (CLI)", style="Dashboard.TButton", command=run_network_manager).grid(
            row=1, column=0, padx=6, pady=(10, 0), sticky="ew"
        )
        ttk.Button(tools_frame, text="Clear Output", style="Dashboard.TButton", command=self.clear_output).grid(
            row=1, column=3, padx=6, pady=(10, 0), sticky="ew"
        )

        output_frame = ttk.LabelFrame(output_tab, text="Output", padding=10, style="Dashboard.TLabelframe")
        output_frame.pack(fill="both", expand=True)

        self.output = ScrolledText(output_frame, wrap="word", font=("Consolas", 11, "normal"))
        self.output.pack(fill="both", expand=True)
        self.output.insert("end", "Welcome to IT Dashboard GUI.\n")
        self.output.insert("end", "Use tabs to navigate features.\n")
        self.output.insert("end", "Neon theme is active across all tabs.\n")
        self.output.configure(state="disabled")

        for col in range(4):
            system_frame.columnconfigure(col, weight=1)
            my_info_frame.columnconfigure(col, weight=1)
            server_frame.columnconfigure(col, weight=1)
            tools_frame.columnconfigure(col, weight=1)

    def refresh_my_info(self):
        """Refresh the date shown in the My Info tab."""
        today = datetime.now().strftime("%m/%d/%Y")
        self.info_date_var.set(f"Date: {today}")

    def refresh_system_info(self):
        """Refresh system info values and reset the next-refresh countdown."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.system_last_refresh_var.set(f"Last refresh: {now}")
        self.system_platform_var.set(
            f"Platform: {platform.system()} {platform.release()} ({platform.machine()})"
        )
        self.system_python_var.set(
            f"Python: {platform.python_version()} ({sys.executable})"
        )
        self.system_cwd_var.set(f"Working directory: {os.getcwd()}")
        self.system_cpu_var.set(f"CPU cores: {os.cpu_count() or 'Unknown'}")

        self.countdown_seconds = self.refresh_interval_seconds
        self.system_countdown_var.set(f"Next refresh in: {self.countdown_seconds}s")

        if self.refresh_job is not None:
            self.root.after_cancel(self.refresh_job)
        self.refresh_job = self.root.after(
            self.refresh_interval_seconds * 1000,
            self.refresh_system_info,
        )

    def update_countdown(self):
        """Update the 1-second countdown indicator between refresh cycles."""
        self.system_countdown_var.set(f"Next refresh in: {max(self.countdown_seconds, 0)}s")
        self.countdown_seconds -= 1
        self.countdown_job = self.root.after(1000, self.update_countdown)

    def start_system_info_auto_refresh(self):
        """Start auto-refresh scheduling for system info and countdown UI."""
        self.refresh_system_info()
        if self.countdown_job is not None:
            self.root.after_cancel(self.countdown_job)
        self.countdown_job = self.root.after(1000, self.update_countdown)

    def on_close(self):
        """Cancel scheduled jobs before closing the app."""
        if self.refresh_job is not None:
            self.root.after_cancel(self.refresh_job)
            self.refresh_job = None
        if self.countdown_job is not None:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        self.root.destroy()

    def apply_theme(self):
        """Apply theme colors to every tab and shared widget."""
        colors = self.get_theme_colors()

        self.root.configure(bg=colors["bg"])
        self.style.theme_use("clam")

        self.style.configure("Dashboard.TFrame", background=colors["bg"])
        self.style.configure(
            "DashboardTitle.TLabel",
            background=colors["bg"],
            foreground=colors["accent"],
            font=("Consolas", 18, "bold"),
        )
        self.style.configure(
            "DashboardMeta.TLabel",
            background=colors["bg"],
            foreground=colors["muted"],
            font=("Consolas", 10, "bold"),
        )
        self.style.configure(
            "Dashboard.TLabel",
            background=colors["surface"],
            foreground=colors["fg"],
            font=("Segoe UI", 10, "normal"),
        )
        self.style.configure(
            "Dashboard.TLabelframe",
            background=colors["surface"],
            borderwidth=1,
            relief="groove",
        )
        self.style.configure(
            "Dashboard.TLabelframe.Label",
            background=colors["surface"],
            foreground=colors["accent"],
            font=("Consolas", 10, "bold"),
        )
        self.style.configure(
            "Dashboard.TButton",
            background=colors["surface_alt"],
            foreground=colors["accent"],
            borderwidth=1,
            relief="flat",
            padding=8,
            font=("Consolas", 10, "bold"),
        )
        self.style.map(
            "Dashboard.TButton",
            background=[("active", colors["accent"]), ("pressed", "#00b7cc")],
            foreground=[("active", "#00131a"), ("pressed", "#00131a")],
        )
        self.style.configure(
            "Dashboard.TEntry",
            fieldbackground=colors["input_bg"],
            foreground=colors["input_fg"],
            borderwidth=1,
            relief="solid",
            font=("Consolas", 10, "normal"),
        )
        self.style.configure(
            "Dashboard.TNotebook",
            background=colors["bg"],
            borderwidth=1,
        )
        self.style.configure(
            "Dashboard.TNotebook.Tab",
            background=colors["surface_alt"],
            foreground=colors["muted"],
            padding=(14, 8),
            font=("Consolas", 10, "bold"),
        )
        self.style.map(
            "Dashboard.TNotebook.Tab",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "#00131a")],
        )

        self.output.configure(
            bg=colors["input_bg"],
            fg=colors["input_fg"],
            insertbackground=colors["input_fg"],
            selectbackground=colors["accent"],
            selectforeground=colors["input_bg"],
        )

        self.theme_label.configure(text="Theme: Neon")

    @staticmethod
    def _add_labeled_entry(parent, label, variable, row, column):
        ttk.Label(parent, text=label, style="Dashboard.TLabel").grid(row=row, column=column, sticky="w", padx=6, pady=4)
        ttk.Entry(parent, textvariable=variable, style="Dashboard.TEntry").grid(
            row=row, column=column + 1, sticky="ew", padx=6, pady=4
        )

    def append_output(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def generate_server_report(self):
        server_name = self.server_name_var.get().strip()
        ip_address = self.ip_address_var.get().strip()
        department = self.department_var.get().strip()

        if not server_name or not ip_address or not department:
            messagebox.showerror("Missing Data", "Server Name, IP Address, and Department are required.")
            return

        try:
            total_disk_gb = int(self.total_disk_var.get().strip())
            used_disk_gb = int(self.used_disk_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Disk values must be integers.")
            return

        if total_disk_gb <= 0:
            messagebox.showerror("Invalid Input", "Total disk must be greater than 0.")
            return
        if used_disk_gb < 0:
            messagebox.showerror("Invalid Input", "Used disk cannot be negative.")
            return
        if used_disk_gb > total_disk_gb:
            messagebox.showerror("Invalid Input", "Used disk cannot exceed total disk.")
            return

        usage_pct = (used_disk_gb / total_disk_gb) * 100
        if usage_pct > 90:
            disk_status = "CRITICAL - Immediate action required"
        elif usage_pct > 75:
            disk_status = "WARNING - Disk usage is elevated"
        else:
            disk_status = "OK - Disk usage is normal"

        report = [
            "=" * 40,
            f"Server Name: {server_name}",
            "=" * 40,
            f"IP Address: {ip_address}",
            f"Department: {department}",
            "-" * 40,
            f"Total Disk Space: {total_disk_gb} GB",
            f"Used Disk Space: {used_disk_gb} GB",
            f"Usage Percentage: {usage_pct:.2f}%",
            f"Disk Status: {disk_status}",
            "=" * 40,
            "System Health Checks:",
            "  - Ping response      : PASS",
            "  - DNS resolution     : PASS",
            "  - Firewall active    : PASS",
        ]
        self.append_output("\n".join(report))

    def run_log_analysis(self):
        ok = analyze_log()
        if not ok:
            messagebox.showerror("Log Analysis", "server.log was not found in the project folder.")
            return

        summary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log_summary.txt")
        try:
            with open(summary_path, "r") as f:
                summary = f.read().strip()
        except FileNotFoundError:
            self.append_output("Log analysis ran, but log_summary.txt could not be read.")
            return

        self.append_output(summary)

    def check_password(self):
        password = self.password_var.get().strip()
        if not password:
            messagebox.showinfo("Password Checker", "Enter a password first.")
            return

        score, rating, feedback = check_password_strength(password, self.common_passwords)
        clean_rating = strip_ansi(rating)
        self.append_output(f"Password score: {score}/6")
        self.append_output(f"Rating: {clean_rating}")
        if feedback:
            self.append_output("Tips:")
            for tip in feedback:
                self.append_output(f"  - {tip}")
        self.append_output("-" * 40)

    def run(self):
        self.root.mainloop()


def run_gui():
    """Launch the Tkinter dashboard UI."""
    app = ITDashboardGUI()
    app.run()


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
        print("6) Password Strength Checker")
        print("7) Exit")

        choice = input("Select an option: ")

        # Prompt for server_name, ip_address, department
        if choice == "1":
            server_name = input ("Server Name : ")
            ip_address = input ("IP Address : ")
            department = input ("Department : ")
            # Prompt for total_disk_gb and used_disk_gb with safe casting
            try:
                total_disk_gb = int(input("Total Disk (GB): "))
                used_disk_gb = int(input("Used Disk (GB): "))
            except ValueError:
                print("\n[!] Error: Disk values must be whole numbers.")
                report_ready = False
                continue
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
                if usage_pct >= 90:
                    disk_status = "CRITICAL - Immediate action required"
                elif usage_pct >= 75:
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
            run_password_checker()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1-7.")
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
        return False

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
    return True


# ── Run the program ───────────────────────────────────────
if __name__ == "__main__":
    main()