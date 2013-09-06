# TODO(Andrey) This code is bad. Fix if PyYaml ever supports outputting comments properly.
class CommentGenerator(object):
	def __init__(self, yml_str):
		self.str = yml_str

	def generate(self):
		lines = self.str.split('\n')

		resulting_lines = []

		resulting_lines.append("# Note that all packages and scripts will be installed/run in their order of appearance.\n")
		resulting_lines.append("# Please look at our documentation page for more information. You can find it at KoalityCode.com/documentation \n\n")
		
		resulting_lines.append("# The first section is language definition, where you define which languages and their respective versions your project uses.\n")

		section = "setup"

		for line in lines:
			if section == "setup":
				if line == "setup:":
					resulting_lines.append("\n# The setup section allows you to define and describe your testing environment.\n")
					resulting_lines.append("setup:\n")
					resulting_lines.append("# The packages section defines dependencies your project needs.\n")
					resulting_lines.append("- packages:\n")
					line = ''

					# The reason for inserting system here is that system requirements cannot be automatically generated and we want to show where they go.
					resulting_lines.append("\n  # Define system package dependencies here. These are all the packages that you use that are installed by running \"apt-get install X\"\n")					
					resulting_lines.append("  - system:")

				elif line == "- packages:":
					line = ''
								

				elif line == "  - pip:":
					resulting_lines.append("\n  # For python, you can also define a requirements.txt file.\n")

				elif line == "  - gem:":
					resulting_lines.append("\n  # For ruby, you can use bundler with a Gemfile.\n")

				elif line == "  - npm:":
					resulting_lines.append("\n  # For nodejs, Npm is used to resolve packages. Packages defined directly under npm are installed globally.\n")

				elif line == "- databases:":
					resulting_lines.append("\n# This section defines databases used for your tests. They are local to the VMs the tests are run on.\n")
					resulting_lines.append("# Currently, only postgres and mysql are supported. This configuration includes both (you can also set passwords).\n")
					
				elif line == "- scripts:":
					resulting_lines .append("\n# In this section you can add shell scripts for any kind of installation operations that you wish to add that were not already covered.\n")
					section = "compile"

				elif line == "compile:":
					resulting_lines .append("\n# In this section you can add shell scripts for any kind of installation operations that you wish to add that were not already covered.\n")
					resulting_lines.append("- scripts:\n")
					resulting_lines.append("\n# The following section defines how to build your code. Each section can be given an arbitrary name.\n")
					section = "compile"


			elif section == "compile":
				if line == "compile:":
					resulting_lines.append("\n# The following section defines how to build your code. Each section can be given an arbitrary name.\n")

				if "  scripts:" in line:
					resulting_lines.append("  # All scripts must return a proper error code (0 for success).\n")

				if line == "test:":
					resulting_lines.append("\n# The test section is responsible for running tests. All commands from here on will be executed in parallel.\n")
					resulting_lines.append("# Remember not to run any scripts that do batch testing from this point on, since they are not parallelizable.\n")
					section = "test"

			elif section == "test":				
				if "machines" in line:
					resulting_lines.append("\n  # The number of VMs to create to run tests on.\n")

				if line == "  factories:":
					resulting_lines.append("  # Factory scripts that will output test scripts to be run in parallel.\n")

			resulting_lines.append(line + "\n")

		return ''.join(resulting_lines)
