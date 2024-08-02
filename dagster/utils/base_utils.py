import os

from jinja2 import Environment


def get_environ(environ_name, default=None):
    result = os.getenv(environ_name, default=default)
    return result


def render_query_with_jinja(query, template_params):
    jinja_env = Environment(extensions=["jinja2.ext.do"])
    if not template_params:
        sqlquery = query
    else:
        tmpl = jinja_env.from_string(query)
        sqlquery = tmpl.render(template_params)
    return sqlquery
