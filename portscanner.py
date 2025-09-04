import socket
import threading
from queue import Queue
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv

# Globals
queue = Queue()
results = []
target = ""

def scan_port(port, text_area):
    """Scans a single port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            status = "Open"
        else:
            status = "Closed"
        results.append([target, port, status])
        text_area.insert(tk.END, f"Port {port}: {status}\n")
        text_area.see(tk.END)
        sock.close()
    except Exception as e:
        text_area.insert(tk.END, f"Error scanning port {port}: {e}\n")

def worker(text_area):
    """Thread worker function"""
    while not queue.empty():
        port = queue.get()
        scan_port(port, text_area)
        queue.task_done()

def save_report():
    """Save results to CSV"""
    if not results:
        messagebox.showwarning("Warning", "No results to save yet!")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"port_scan_report_{timestamp}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Target", "Port", "Status"])
        writer.writerows(sorted(results, key=lambda x: x[1]))
    messagebox.showinfo("Saved", f"✅ Report saved as {filename}")

def start_scan(target_entry, ports_entry, text_area):
    global target, results
    results = []
    target = target_entry.get().strip()
    port_range = ports_entry.get().strip()

    if not target or not port_range:
        messagebox.showwarning("Input Error", "Please enter target and port range")
        return

    try:
        start_port, end_port = map(int, port_range.split("-"))
    except:
        messagebox.showwarning("Input Error", "Port range must be in format: 20-100")
        return

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, f"🚀 Starting scan on {target} ({start_port}-{end_port})...\n")

    # Fill queue
    for port in range(start_port, end_port + 1):
        queue.put(port)

    # Start threads
    thread_count = 50
    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(text_area,))
        t.daemon = True
        t.start()

    threading.Thread(target=queue.join).start()

# ---------------- GUI ----------------
def main():
    root = tk.Tk()
    root.title("CyberSec Port Scanner")
    root.geometry("600x400")

    # Input fields
    tk.Label(root, text="Target (IP or domain):").pack()
    target_entry = tk.Entry(root, width=50)
    target_entry.pack(pady=5)

    tk.Label(root, text="Port Range (e.g. 20-100):").pack()
    ports_entry = tk.Entry(root, width=50)
    ports_entry.pack(pady=5)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    scan_btn = ttk.Button(btn_frame, text="Start Scan", command=lambda: start_scan(target_entry, ports_entry, text_area))
    scan_btn.grid(row=0, column=0, padx=5)

    save_btn = ttk.Button(btn_frame, text="Save Report", command=save_report)
    save_btn.grid(row=0, column=1, padx=5)

    # Output box
    text_area = tk.Text(root, height=15, width=70)
    text_area.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
