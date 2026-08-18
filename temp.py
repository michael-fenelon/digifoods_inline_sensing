import logging
from datetime import*
import sys

if sys.platform == "win32":
    print("Running on Windows")
elif sys.platform.startswith("linux"):
    print("Running on Linux")
else:
    print(f"Running on another OS: {sys.platform}")


# prefix = datetime.now()
# print(datetime.now())
# logging.basicConfig(filename=str(prefix) + "_Log.log",
#                     format='%(asctime)s %(levelname)s: %(message)s',
#                     filemode='w')

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# logger.debug("Harmless debug message")
# logger.info("Just an information")
# logger.warning("Its a warning")
# logger.error("Did you try to divide by zero?")
# logger.critical("Internet is down")




