import random
import time
import schedule
import threading
from datetime import datetime, date
from typing import List
import json
import os
import sys
import platform
import subprocess
import shutil
from plyer import notification

from quote import quote_list, _quote

class PersistentQuoteManager:
    def __init__(self, quotes: List[_quote], data_file: str = "quote_data.json"):
        self.quotes = quotes
        self.data_file = data_file
        self.load_state()
    
    def load_state(self):
        """Load the last shown quote and date from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.last_date = datetime.strptime(data['last_date'], '%Y-%m-%d').date()
                    self.last_quote_index = data['last_quote_index']
                    print(f"Loaded state: last quote shown on {self.last_date}")
            except (json.JSONDecodeError, KeyError):
                # File exists but corrupted, initialize fresh
                self.initialize_state()
        else:
            self.initialize_state()
    
    def initialize_state(self):
        """Initialize with today's date and no previous quote"""
        self.last_date = date.today()
        self.last_quote_index = -1
        print("Initialized new quote state")
    
    def save_state(self):
        """Save current state to file"""
        data = {
            'last_date': self.last_date.isoformat(),
            'last_quote_index': self.last_quote_index
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f)
    
    def get_daily_quote(self) -> _quote:
        """Get today's quote (same quote all day)"""
        print("Downloading Updates...")
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True)
            if result.stderr:
                resp = input("Clone from repository? [Y/n]")
                if resp.lower().strip() in ("n", "no"):
                    print("Will not clone.")
                else:
                    result = subprocess.run(["git", "clone", "https://github.com/Eddy12597/JordiQuotes.git"],
                                        capture_output=True,
                                        text=True)
            if result.stderr:
                print(f"An error occurred during 'git pull': {result.stderr}")
                if platform.system() == "Darwin":
                    resp = input("Run 'brew install git'? [Y/n]")
                    if resp.lower().strip() in ("n", "no"):
                        print("Will not install.")
                    else:
                        print("Installing: 'brew install git'")
                        gitinstallresult = subprocess.run(["brew", "install", "git"], text=True, capture_output=True)
                        if gitinstallresult.stderr:
                            print(f"An Error occurred during 'brew install git': {result.stderr}")
                        else:
                            print(f"Successfully installed git. Downloading updates...")
                            gitpullafterinstresult = subprocess.run(["cd .. && git clone https://github.com/Eddy12597/JordiQuotes.git && cd JordiQuotes"], shell=True, capture_output=True, text=True)
                            if gitpullafterinstresult.stderr:
                                print(f"An error occurred during 'git clone ...' after git is installed: {gitpullafterinstresult.stderr}")
                            else:
                                print(f"Successfully updated")
                elif platform.system() == "Windows":
                    resp = input("Install git via cURL? [Y/n]")
                    if resp.lower().strip() in ("n", "no"):
                        print("Will not install.")
                    else:
                        print("running command:")
                        print('curl -L -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe; Start-Process git-installer.exe -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS", "/COMPONENTS=icons,ext\\reg\\shellhere,assoc,assoc_sh" -Wait')
                        wininstres = subprocess.run('curl -L -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe && Start-Process git-installer.exe -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS", "/COMPONENTS=icons,ext\\reg\\shellhere,assoc,assoc_sh" -Wait')
                        if wininstres.stderr:
                            print(f"An error occurred: {wininstres.stderr}")
                        else:
                            print(f"Git installed. Cloning repository...")
                            clretr = subprocess.run(["git", "clone", "https://github.com/Eddy12597/JordiQuotes"])
                            if clretr.stderr:
                                print(f"An error occurred in cloning after git is installed: {clretr.stderr}")
                            else:
                                print(f"Update complete!")
                elif platform.system() == "Linux":
                    import distro
                    if distro.name() == "Arch Linux":
                        print("Distro: Arch Linux. I also use arch btw.")
                        archgitres = subprocess.run(["sudo", "pacman", "-S", "git"])
                        if archgitres.stderr:
                            print(f"An error occurred: {archgitres.stderr}")
                            
            else:
                print("Update complete!")
            
        except Exception as e:
            print("An error occurred during update:", str(e))
            

        today = date.today()
        
        # If we already showed a quote today, return the same one
        if today == self.last_date and self.last_quote_index != -1:
            return self.quotes[self.last_quote_index]
        
        # New day - get new random quote (consistent for the day)
        self.last_date = today
        random.seed(today.toordinal())  # Same seed for entire day
        self.last_quote_index = random.randint(0, len(self.quotes) - 1)
        self.save_state()
        
        new_quote = self.quotes[self.last_quote_index]
        print(f"New daily quote selected: {new_quote.origin}")
        return new_quote
    
    def get_random_quote(self) -> _quote:
        """Get a completely random quote (for manual requests)"""
        return random.choice(self.quotes)

def show_macos_notification(quote: _quote):
    """Show macOS notification using terminal-notifier or AppleScript fallback"""
    message = str(quote)
    if len(message) > 200:
        message = message[:197] + "..."
    
    # Escape quotes for shell commands
    escaped_message = message.replace('"', '\\"').replace('`', '\\`')
    escaped_origin = quote.origin.replace('"', '\\"').replace('`', '\\`')
    
    # Try terminal-notifier first (most reliable)
    if shutil.which('terminal-notifier'):
        try:
            subprocess.run([
                'terminal-notifier',
                '-title', '📖 Daily Quote',
                '-subtitle', escaped_origin,
                '-message', escaped_message,
                '-sound', 'default',
                '-timeout', '15'
            ], check=True, capture_output=True)
            print(f"Notification shown via terminal-notifier: {quote.origin}")
            return
        except subprocess.CalledProcessError as e:
            print(f"terminal-notifier failed: {e}")
    
    # Fallback to AppleScript
    try:
        applescript = f'''
        display notification "{escaped_message}" with title "📖 Daily Quote" subtitle "{escaped_origin}" sound name "default"
        '''
        subprocess.run(['osascript', '-e', applescript], check=True, capture_output=True)
        print(f"Notification shown via AppleScript: {quote.origin}")
    except subprocess.CalledProcessError as e:
        print(f"AppleScript notification failed: {e}")
        # Ultimate fallback - just print
        print("🔔 Daily Quote Notification (Fallback):")
        print(f"📖 {message}")
        print(f"📍 {quote.origin}")

def show_windows_notification(quote: _quote):
    """Show Windows notification using plyer"""
    try:
        message = str(quote)
        if len(message) > 200:
            message = message[:197] + "..."
        
        notification.notify(
            title="📖 Daily Quote",
            message=message,
            timeout=15,
            app_name="Quote App",
            toast=True
        )
        print(f"Notification shown: {quote.origin}")
    except Exception as e:
        print(f"Error showing Windows notification: {e}")

def show_linux_notification(quote: _quote):
    """Show Linux notification using plyer or notify-send"""
    message = str(quote)
    if len(message) > 200:
        message = message[:197] + "..."
    
    try:
        notification.notify(
            title="📖 Daily Quote",
            message=message,
            timeout=15,
            app_name="Quote App"
        )
        print(f"Notification shown via plyer: {quote.origin}")
    except Exception:
        # Fallback to notify-send
        try:
            subprocess.run([
                'notify-send',
                '📖 Daily Quote',
                f'{message}\n\n— {quote.origin}',
                '-t', '15000',  # 15 seconds
                '-i', 'dialog-information'
            ], check=True)
            print(f"Notification shown via notify-send: {quote.origin}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Linux notification failed: {e}")
            print("🔔 Daily Quote (Fallback):", message)

def show_notification(quote: _quote):
    """Show desktop notification with platform-specific handling"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        show_macos_notification(quote)
    elif system == "Windows":
        show_windows_notification(quote)
    else:  # Linux and other Unix-like systems
        show_linux_notification(quote)

def print_quote(quote: _quote):
    """Print quote to console"""
    print("\n" + "="*60)
    print("DAILY QUOTE")
    print("="*60)
    print(quote)
    print("="*60 + "\n")

# =============================================
# DIFFERENT SCHEDULING STRATEGIES
# =============================================

def run_simple_scheduler(manager: PersistentQuoteManager, notification_time: str = "09:00"):
    """
    Strategy 1: Using schedule library (recommended)
    Most flexible and reliable
    """
    print(f"Starting simple scheduler - quotes will show daily at {notification_time}")
    
    # Show immediate quote on startup
    quote = manager.get_daily_quote()
    show_notification(quote)
    print_quote(quote)
    
    # Schedule daily notification
    schedule.every().day.at(notification_time).do(
        lambda: show_notification(manager.get_daily_quote())
    )
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute - low CPU
    except KeyboardInterrupt:
        print("\nStopping quote scheduler...")

def run_sleep_scheduler(manager: PersistentQuoteManager):
    """
    Strategy 2: Simple sleep-based scheduler
    Low CPU but less flexible
    """
    print("Starting sleep-based scheduler - 24-hour intervals")
    
    while True:
        try:
            quote = manager.get_daily_quote()
            show_notification(quote)
            print_quote(quote)
            
            # Wait 24 hours
            print("Waiting 24 hours for next quote...")
            time.sleep(24 * 60 * 60)  # 24 hours
            
        except KeyboardInterrupt:
            print("\nStopping quote scheduler...")
            break
        except Exception as e:
            print(f"Error in scheduler: {e}")
            time.sleep(300)  # Wait 5 minutes before retry

def run_threaded_scheduler(manager: PersistentQuoteManager, notification_time: str = "09:00"):
    """
    Strategy 3: Threaded scheduler with graceful shutdown
    """
    class QuoteScheduler:
        def __init__(self, manager):
            self.manager = manager
            self.running = False
            self.thread = None
        
        def start(self):
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            print(f"Threaded scheduler started - daily at {notification_time}")
        
        def stop(self):
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
        
        def _run(self):
            # Immediate quote on startup
            quote = self.manager.get_daily_quote()
            show_notification(quote)
            print_quote(quote)
            
            while self.running:
                try:
                    schedule.every().day.at(notification_time).do(
                        lambda: show_notification(self.manager.get_daily_quote())
                    )
                    
                    # Check schedule every minute
                    for _ in range(60):  # 60 minutes
                        if not self.running:
                            return
                        schedule.run_pending()
                        time.sleep(60)
                        
                except Exception as e:
                    print(f"Scheduler error: {e}")
                    time.sleep(60)
    
    scheduler = QuoteScheduler(manager)
    scheduler.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping threaded scheduler...")
        scheduler.stop()

# =============================================
# MAIN APPLICATION
# =============================================

def main():
    # Initialize quote manager
    manager = PersistentQuoteManager(quote_list)
    
    print(f"Loaded {len(quote_list)} quotes")
    print(f"Platform: {platform.system()}")
    print("Daily Quote Application")
    print("=" * 40)
    
    # Platform-specific notification info
    if platform.system() == "Darwin":
        print("💡 macOS: Using terminal-notifier with AppleScript fallback")
        if not shutil.which('terminal-notifier'):
            print("💡 Install terminal-notifier for better notifications:")
            print("   brew install terminal-notifier")
    print("=" * 40)
    
    print("1. Run with schedule library (recommended)")
    print("2. Run with simple sleep scheduler")
    print("3. Run with threaded scheduler")
    print("4. Show today's quote once and exit")
    print("5. Show random quote")
    print("6. Test notification")
    print("=" * 40)
    
    try:
        choice = input("Choose option ([1]-6): ").strip()
            
        if choice == "2":
            run_sleep_scheduler(manager)
            
        elif choice == "3":
            time_str = input("Enter notification time (HH:MM) [07:59]: ").strip()
            notification_time = time_str if time_str else "07:59"
            run_threaded_scheduler(manager, notification_time)
            
        elif choice == "4":
            quote = manager.get_daily_quote()
            print_quote(quote)
            
        elif choice == "5":
            quote = manager.get_random_quote()
            print("\nRANDOM QUOTE:")
            print_quote(quote)
            
        elif choice == "6":
            quote = manager.get_daily_quote()
            show_notification(quote)
            print_quote(quote)
            print("Notification test completed")
            
        else:
            time_str = input("Enter notification time (HH:MM) [07:59]: ").strip()
            notification_time = time_str if time_str else "07:59"
            run_simple_scheduler(manager, notification_time)
            
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()