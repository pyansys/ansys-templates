# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the problem setup step."""
import platform

from pathlib import Path

from ansys.saf.glow.solution import StepModel, StepSpec, transaction, FileReference #, long_running
from ansys.solutions.optislang.parser.placeholder import ProjectProperties
from ansys.solutions.products_ecosystem.utils import convert_to_long_version
from ansys.solutions.products_ecosystem.controller import AnsysProductsEcosystemController

class ProblemSetupStep(StepModel):

    placeholder_values = {}
    placeholder_definitions = {}
    optislang_solve_status: str = "initial"  # initial, in-progress, failure, success
    ansys_ecosystem_checked: bool = False
    ansys_ecosystem: dict = {
        "optislang": {
            "authorized_versions": ["2022.2", "2023.1"],
            "installed_versions": [],
            "compatible_versions": [],
            "selected_version": None,
            "alert_message": "OptiSLang install not checked.",
            "alert_color": "warning"
        },
    }
    run_synchronously: bool = True

    # File storage
    project_file: FileReference = FileReference("Problem_Setup/{{ cookiecutter.__optiSLang_project_file_name }}")
    properties_file: FileReference = FileReference("Problem_Setup/{{ cookiecutter.__optiSLang_properties_file_name }}")

    @transaction(self=StepSpec(download=["properties_file"], upload=["placeholder_values", "placeholder_definitions"]))
    def get_default_placeholder_values(self):
        """Get placeholder values and definitions using the ProjectProperties class."""

        pp = ProjectProperties()
        pp.read_file(self.properties_file.path)
        placeholders = pp.get_properties()['placeholders']
        self.placeholder_values = placeholders.get('placeholder_values')
        self.placeholder_definitions = placeholders.get('placeholder_definitions')

    @transaction(self=StepSpec(upload=["project_file"]))
    def upload_project_file_to_project_directory(self) -> None:
        """Upload OptiSLang project file to project directory."""

        original_project_file = (
            Path(__file__).parent.absolute().parent / "model" / "assets" / "{{ cookiecutter.__optiSLang_project_file_name }}"
        )
        self.project_file.write_bytes(original_project_file.read_bytes())

    @transaction(self=StepSpec(upload=["properties_file"]))
    def upload_properties_file_to_project_directory(self) -> None:
        """Upload OptiSLang properties to project directory."""

        original_properties_file = (
            Path(__file__).parent.absolute().parent / "model" / "assets" / "{{ cookiecutter.__optiSLang_properties_file_name }}"
        )
        self.properties_file.write_bytes(original_properties_file.read_bytes())

    @transaction(
        self=StepSpec(
            upload=["ansys_ecosystem"],
        )
    )
    def check_ansys_ecosystem(self) -> None:
        """Check if Ansys Products are installed and if the appropriate versions are available."""

        controller = AnsysProductsEcosystemController()

        for product_name in self.ansys_ecosystem.keys():
            self.ansys_ecosystem[product_name]["installed_versions"] = controller.get_installed_versions(product_name, outout_format="long")
            self.ansys_ecosystem[product_name]["compatible_versions"] = [product_version for product_version in self.ansys_ecosystem[product_name]["installed_versions"] if product_version in self.ansys_ecosystem[product_name]["authorized_versions"]]

            if len(self.ansys_ecosystem[product_name]["installed_versions"]) == 0:
                alert_message = f"No installation of {product_name.title()} found in the machine {platform.node()}."
                alert_color = "danger"
            elif len(self.ansys_ecosystem[product_name]["compatible_versions"]) == 0:
                alert_message = f"None of the authorized versions of {product_name.title()} is installed in the machine {platform.node()}.\n"
                alert_message += "At least one of these versions is required:"
                for authorized_version in self.ansys_ecosystem[product_name]["authorized_versions"]:
                    self.ansys_ecosystem[product_name]["alert_message"] += f" {convert_to_long_version(authorized_version)}"
                alert_message += "."
                alert_color = "danger"
            else:
                self.ansys_ecosystem[product_name]["selected_version"] = self.ansys_ecosystem[product_name]["compatible_versions"][-1] #Latest
                alert_message = f"{product_name.title()} install detected. Compatible versions are:"
                for compatible_version in self.ansys_ecosystem[product_name]["compatible_versions"]:
                    alert_message += f" {convert_to_long_version(compatible_version)}"
                alert_message += ".\n"
                alert_message += "Selected version is %s." % (self.ansys_ecosystem[product_name]["selected_version"])
                alert_color = "success"
            self.ansys_ecosystem[product_name]["alert_message"] = alert_message
            self.ansys_ecosystem[product_name]["alert_color"] = alert_color

        self.ansys_ecosystem_checked = True

    # @transaction(
    #     self=StepSpec(
    #         download=[
    #             "ansys_ecosystem",
    #             "project_file",
    #             "properties_file",
    #             "workbench_input_deck"
    #         ],
    #         upload=[
    #             "optislang_solve_status",
    #             "results_directory",
    #             "best_design_file"
    #         ],
    #     )
    # )
    # @long_running
    # def run_optislang(self) -> None:
    #     """Start OptiSLang and run the project."""

    #     stderr_file = str(self.project_file.project_path / "Problem_Setup" / "stderr.log")

    #     # Start OptiSLang
    #     osl = OptiSLangOrchestrator(
    #         project_file = self.project_file.path,
    #         properties_file = self.properties_file.path,
    #         output_file = "hook_optimization_output.json",
    #         version = convert_to_short_version(self.ansys_ecosystem["optislang"]["selected_version"])
    #     )
    #     osl.start()

    #     # Wait for OptiSLang to complete
    #     while True:
    #         # Check the status of the OptiSLang solve
    #         if osl.get_status() == "processing":
    #             self.optislang_solve_status = "in-progress"
    #         elif osl.get_status() == "succeeded":
    #             self.optislang_solve_status = "success"
    #         elif osl.get_status() == "failed":
    #             self.optislang_solve_status = "failure"
    #         elif osl.get_status() == "stopped": # Case where OptiSLang stops without error, to further continue the solve.
    #             if not check_if_file_is_empty(stderr_file):
    #                 self.optislang_solve_status = "failure"
    #         else:
    #             osl.stop()
    #             raise Exception(f"ERROR: Unknown status: {osl.get_status()}.")
    #         # Exit
    #         if osl.get_status() == "succeeded" or self.optislang_solve_status == "failure":
    #             osl.stop()
    #             break
    #         time.sleep(1)

    #     pause = True
