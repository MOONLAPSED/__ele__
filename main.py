# assume setup.py is in the same directory as src and src/__init__.py
# assume setup.py has invoked ele/src/lager.py and cognic/src/__init__.py
# assume setup.py has invoked ele/main.py (this script)
import sys
import subprocess
from src.lager import Lager
from pydantic import BaseModel, Field

# dont need these if I import 
import logging
from datetime import datetime, date
import os

"""main handles setting launch and state environment variables and running the runtime of the working application."""

def runtime(lager):
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "--verify", "HEAD"]).decode().strip()
        return git_hash

    except subprocess.CalledProcessError as e:
        if "fatal: not a git repository" in e.output.decode():
            lager.warning("No Git repository found. Skipping Git info.")
            return None
        else:
            raise  # Re-raise other Git errors for debugging

class MySettings(BaseModel):
    required_date: date = Field(default_factory=datetime.now().date)
    required_int: int = Field(0, ge=0)  # Set default value here
    state: int = Field(0)  # New field to hold the state value

    def __init__(self):
        super().__init__()
        try:
            self.required_int = int(os.getenv("REQUIRED_INT", default=0))
            self.state = int(os.getenv("STATE", default=0))  # Load 'state' from .env file
        except Exception as e:
            logging.basicConfig(filename='/logs/setup.log', level=logging.ERROR)
            logging.error(f"Error loading environment variables: {e}", exc_info=True)
            raise  # Re-raise the exception to halt execution

if __name__ == "__main__":
    rt = None
    settings = MySettings()
    settings.state = 1  # Set the state to 1 to indicate runtime pydantic validation has completed
    with open('.env', 'w') as env_file:  # Update state in .env file
        env_file.write(f"STATE={settings.state}\n")
    try:
        if 'lager' not in locals():
            lager = Lager()  # Create an instance of the logger
        else:
            lager = locals()['lager']  # Retrieve the logger instance from the locals() dictionary
        rt = runtime(lager)  # Pass the logger instance to the runtime function

        if rt is not None:  # Check if Git info was retrieved
            git_hash = rt
        else:
            git_hash = None

        if rt is None:
            lager.warning("Git initialization skipped in __main__")
        
    except ImportError:
        print("src not found, try reinstalling the package or running the setup.py script")
        settings.state = -1 # Set state to -1 to indicate runtime pydantic validation has failed
        sys.exit(1)
    except Exception as e:
        print(e)
    finally:
        # ...
        if rt is None:
            stdout=subprocess.PIPE
            stderr=subprocess.PIPE
            if "fatal: not a git repository" in str(stdout):
                print("fatal: not a git repository, now is your chance to ctrl+c because Ima chargin mah lazor!")
                # git init functionality
            else: # this is the default case
                # async.wait loop for runtime's return value
                # ...                
                pass

    settings.state = 0  # pydantic validation init and app has achieved runtime, set state to 0 (for possible re-initialization/debugging)
    with open('.env', 'w') as env_file:  # Update state in .env file
        env_file.write(f"STATE={settings.state}\n")
    sys.exit(0)
else:
    print("You have no src directory so please run /ele/setup.py directly")
    sys.exit(1)