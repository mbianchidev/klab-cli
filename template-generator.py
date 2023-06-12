import os
import argparse
import logging
import yaml
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)
# TODO it needs to be completely reworked

class TemplateGenerator:
    CUR_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    DIR_PATH_TF = os.path.abspath(os.path.join(CUR_DIR_PATH, 'AWS', 'S3'))
    DIR_PATH_KB = os.path.abspath(os.path.join(CUR_DIR_PATH, '..', 'Modules', 'Kubernetes'))
    DIR_PATH_CF = os.path.abspath(os.path.join(CUR_DIR_PATH, '..', 'Modules', 'CloudFormation'))

    @staticmethod
    def gen_tf_template(template):
        """
        Generate Terraform template.

        :param template: Name of the template file
        :return: Generated Terraform template content
        """
        try:
            with open(os.path.join(TemplateGenerator.DIR_PATH_TF, template)) as file:
                conf_var = yaml.safe_load(file)

            file_loader = FileSystemLoader([os.path.join(TemplateGenerator.DIR_PATH_TF)])

            env = Environment(loader=file_loader, autoescape=True)

            jinja_template = env.get_template(conf_var['template_path'])
            output = jinja_template.render(conf_var)

            with open(os.path.join(TemplateGenerator.DIR_PATH_TF, 'Testing', 'output-tf.tf'), 'w') as f:
                f.write(output)
            return output
        except Exception as err:
            logging.exception("Can't generate Terraform template")
            return str(err)

    @staticmethod
    def gen_kub_template(template):
        """
        Generate Kubernetes template.

        :param template: Name of the template file
        :return: Generated Kubernetes template content
        """
        try:
            with open(os.path.join(TemplateGenerator.DIR_PATH_KB, template)) as file:
                conf_var = yaml.safe_load(file)

            file_loader = FileSystemLoader([os.path.join(TemplateGenerator.DIR_PATH_KB)])

            env = Environment(loader=file_loader, autoescape=True)

            jinja_template = env.get_template(conf_var['template_path'])
            output = jinja_template.render(conf_var)

            with open(os.path.join(TemplateGenerator.DIR_PATH_KB, 'output-templates', 'output-kb.tf'), 'w') as f:
                f.write(output)
            return output
        except Exception as err:
            logging.exception("Can't generate Kubernetes template")
            return str(err)

    @staticmethod
    def gen_cf_template(template):
        """
        Generate CloudFormation template.

        :param template: Name of the template file
        :return: Generated CloudFormation template content
        """
        try:
            with open(os.path.join(TemplateGenerator.DIR_PATH_CF, 'conf', template)) as file:
                conf_var = yaml.safe_load(file)

            file_loader = FileSystemLoader([os.path.join(TemplateGenerator.DIR_PATH_CF, 'templates')])

            env = Environment(loader=file_loader, autoescape=True)

            jinja_template = env.get_template(conf_var['template_path'])
            output = jinja_template.render(conf_var)

            with open(os.path.join(TemplateGenerator.DIR_PATH_CF, 'templates', 'CodePipeline', 'output.yaml'), 'w') as f:
                f.write(output)
            return output
        except Exception as err:
            logging.exception("Can't generate CloudFormation template")
            return str(err)

    @staticmethod
    def parse_arguments():
        """
        Parse command-line arguments.

        :return: Parsed arguments
        """
        parser = argparse.ArgumentParser(description='Generate or deploy AWS Stack')
        parser.add_argument("--terraform", "-tf", help="Generate Terraform template", action="store")
        parser.add_argument("--kubernetes", "-k", help="Generate Kubernetes template", action="store")
        parser.add_argument("--cloudformation", "-cf", help="Generate CloudFormation template", action="store")
        return parser.parse_args()

    def run(self):
        """
        Run the template generator based on command-line arguments.
        """
        args = self.parse_arguments()
        logging.info(args)

        if args.terraform:
            print(TemplateGenerator.gen_tf_template(args.terraform))
        elif args.kubernetes:
            print(TemplateGenerator.gen_kub_template(args.kubernetes))
        elif args.cloudformation:
            print(TemplateGenerator.gen_cf_template(args.cloudformation))
        else:
            logging.info("Choose an option")


if __name__ == '__main__':
    template_generator = TemplateGenerator()
    template_generator.run()
