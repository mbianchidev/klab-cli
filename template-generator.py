import os
import argparse
import logging
import yaml
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)


class TemplateGenerator:
    CUR_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    TESTING_DIR = os.path.abspath(os.path.join(CUR_DIR_PATH, 'Testing'))

    def gen_tf_template(self, cloud_provider, module, conf_file):
        """
        Generate Terraform template.

        :param cloud_provider: Cloud provider name
        :param module: Module name
        :param conf_file: Name of the configuration file
        :return: Generated Terraform template content
        """
        try:
            dir_path_tf = os.path.abspath(os.path.join(TemplateGenerator.CUR_DIR_PATH, cloud_provider, module))
            conf_path = os.path.join(dir_path_tf, f'{conf_file}.yaml')

            with open(conf_path) as file:
                conf_var = yaml.safe_load(file)

            file_loader = FileSystemLoader(dir_path_tf)

            env = Environment(loader=file_loader, autoescape=True)

            jinja_template = env.get_template(conf_var['template_path'])
            output = jinja_template.render(conf_var)

            os.makedirs(TemplateGenerator.TESTING_DIR, exist_ok=True)
            output_path = os.path.join(TemplateGenerator.TESTING_DIR, f'{conf_file}-output-tf.tf')
            with open(output_path, 'w') as f:
                f.write(output)

            return output
        except Exception as err:
            logging.exception("Can't generate Terraform template")
            return str(err)

    def parse_arguments(self):
        """
        Parse command-line arguments.

        :return: Parsed arguments
        """
        parser = argparse.ArgumentParser(description='Generate or deploy AWS Stack')
        parser.add_argument("--cloud-provider", "-c", help="Cloud provider name", required=True)
        parser.add_argument("--module", "-m", help="Module name", required=True)
        parser.add_argument("--terraform", "-tf", help="Generate Terraform template", required=True)
        return parser.parse_args()

    def run(self):
        """
        Run the template generator based on command-line arguments.
        """
        args = self.parse_arguments()
        logging.info(args)

        self.gen_tf_template(args.cloud_provider, args.module, args.terraform)


if __name__ == '__main__':
    template_generator = TemplateGenerator()
    template_generator.run()