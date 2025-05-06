
#?  The primary purpose of an __init__.py file (even an empty one) is to tell the Python interpreter that the directory containing it should be treated as a Python package (or sub-package).
#?  This allows you to import modules from that directory using dot notation. For example, having src/__init__.py lets you do imports like import src.scrapers.player_url_finder or from src.tasks 
#?  import scrape_tasks. Without __init__.py in the src and tasks directories, these kinds of imports would generally fail.