# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Initialization of the frontend layout across all the steps."""

from ansys.saf.glow.client.dashclient import DashClient
from ansys_dash_treeview import AnsysDashTreeview
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, callback, callback_context, dcc, html
from dash_iconify import DashIconify

from ansys.solutions.{{ cookiecutter.__solution_name_slug }}.solution.definition import {{ cookiecutter.__solution_name_slug }}Solution
from ansys.solutions.{{ cookiecutter.__solution_name_slug }}.ui.pages import monitoring_page, problem_setup_page
from ansys.solutions.{{ cookiecutter.__solution_name_slug }}.ui.utils.common_functions import extract_dict_by_key, read_system_hierarchy

step_list = read_system_hierarchy()


layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # represents the browser address bar and doesn't render anything
        dbc.Stack(
            [
                html.Div(
                    [html.Img(src=r"/assets/logos/ansys-solutions-horizontal-logo.png", style={"width": "80%"})],
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Project Name:",
                            id="project-name",
                            disabled=True,
                            style={
                                "color": "rgba(0, 0, 0, 1)",
                                "background-color": "rgba(255, 255, 255, 1)",
                                "border-color": "rgba(0, 0, 0, 1)",
                            },
                        )
                    ],
                    className="ms-auto",
                ),
                html.Div(id="return-to-portal"),
            ],
            direction="horizontal",
            gap=3,
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    AnsysDashTreeview(
                        id="navigation_tree",
                        items=step_list,
                        children=[
                            DashIconify(icon="bi:caret-right-square-fill"),
                            DashIconify(icon="bi:caret-down-square-fill"),
                        ],
                        style={"showButtons": True, "focusColor": "#ffb71b", "itemHeight": "32"},  # Ansys gold
                    ),
                    width=2,
                    style={"background-color": "rgba(242, 242, 242, 0.6)"},  # Ansys grey
                ),
                dbc.Col(html.Div(id="page-content", style={"padding-right": "1%"}), width=10),
            ],
        ),
    ]
)


@callback(
    Output("return-to-portal", "children"),
    Input("url", "pathname"),
)
def return_to_portal(pathname):
    """Display Solution Portal when back-to-portal button gets selected."""
    portal_ui_url = DashClient.get_portal_ui_url()
    children = (
        []
        if portal_ui_url is None
        else [
            dbc.Button(
                "Back to Projects",
                id="return-to-portal",
                className="me-2",
                n_clicks=0,
                href=portal_ui_url,
                style={"background-color": "rgba(0, 0, 0, 1)", "border-color": "rgba(0, 0, 0, 1)"},
            )
        ]
    )
    return children


@callback(
    Output("project-name", "children"),
    Input("url", "pathname"),
)
def display_poject_name(pathname):
    """Display current project name."""
    project = DashClient[{{ cookiecutter.__solution_name_slug }}Solution].get_project(pathname)
    return f"Project Name: {project.project_display_name}"


@callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input("navigation_tree", "focus"),
    ],
    prevent_initial_call=True,
)
def display_page(pathname, value):
    """
    Display page content.

    this callback is essential for initializing the step based on the persisted
    state of the project when the browser first displays the project to the user
    given the project's URL
    """

    project = DashClient[{{ cookiecutter.__solution_name_slug }}Solution].get_project(pathname)
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "url":
        return problem_setup_page.layout(project.steps.problem_setup_step)
    if triggered_id == "navigation_tree":
        if value is None:
            page_layout = html.H1("Welcome!")
        elif value == "problem_setup_step":
            page_layout = problem_setup_page.layout(project.steps.problem_setup_step)
        else:
            node_info = extract_dict_by_key(step_list, "key", value, expect_unique=True)
            page_layout = monitoring_page.layout(
                project.steps.problem_setup_step, project.steps.monitoring_step, node_info
            )
        return page_layout
