from jinja2 import Environment, FileSystemLoader
import datetime

env = Environment(loader=FileSystemLoader("digest/templates"))

def build_html(stories: list) -> str:
    tmpl = env.get_template("digest.html")
    return tmpl.render(
        stories=stories,
        date=datetime.date.today().strftime("%B %d, %Y"),
        next_run="in 2 hours"
    )