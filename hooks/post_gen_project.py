# -*- coding: utf-8 -*-

"""
Finish a generated project:

- Write LICENSE.txt. The template is for closed source projects, so it is
  always the proprietary license, whatever the SPDX expression in ``license``,
  with the current year and the project's author.
- Copy the git-ignored local files (.env, config/config-*-secret.json5) from
  their examples and fill in the AWS account ids.
"""

import shutil
from pathlib import Path

dir_project_root = Path.cwd()

proprietary_license = """
Copyright (c) {% now 'utc', '%Y' %} {{ cookiecutter.author }} <{{ cookiecutter.author_email }}>

All rights reserved.

This software is proprietary and confidential. Unauthorized copying, modification, distribution, or use of this software, in whole or in part, is strictly prohibited unless prior written permission is obtained from the copyright holder.

This software is provided "as is" without warranty of any kind, either express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

For licensing inquiries or commercial use, please contact: {{ cookiecutter.author }} <{{ cookiecutter.author_email }}>.
""".strip()

dir_project_root.joinpath("LICENSE.txt").write_text(proprietary_license, encoding="utf-8")

# Local, per-person settings, git-ignored in the generated project: copy each
# example once so the project is ready to fill in. Keep in sync with
# HOOK_OUTPUTS in .mise/tasks/make_template.py.
local_files = {
    ".env": ".env.example",
    "config/config-shared-secret.json5": "config/example/config-shared-secret.json5.example",
    "config/config-dev-secret.json5": "config/example/config-dev-secret.json5.example",
    "config/config-tst-secret.json5": "config/example/config-dev-secret.json5.example",
    "config/config-prd-secret.json5": "config/example/config-dev-secret.json5.example",
}
for dst, src in local_files.items():
    path_dst = dir_project_root.joinpath(dst)
    if not path_dst.exists():
        shutil.copyfile(dir_project_root.joinpath(src), path_dst)

# Fill in the AWS account ids: replace the placeholder id of each example.
# Keep in sync with devops_aws_account_id and HOOK_VARIABLES in
# .mise/tasks/make_template.py.
aws_account_ids = {
    "config/config-shared-secret.json5": ("111122223333", "{{ cookiecutter.devops_aws_account_id }}"),
    "config/config-dev-secret.json5": ("123456789012", "{{ cookiecutter.dev_aws_account_id }}"),
    "config/config-tst-secret.json5": ("123456789012", "{{ cookiecutter.tst_aws_account_id }}"),
    "config/config-prd-secret.json5": ("123456789012", "{{ cookiecutter.prd_aws_account_id }}"),
}
for dst, (placeholder, account_id) in aws_account_ids.items():
    path_dst = dir_project_root.joinpath(dst)
    text = path_dst.read_text(encoding="utf-8")
    path_dst.write_text(text.replace(f'"{placeholder}"', f'"{account_id}"'), encoding="utf-8")

files = "\n".join(f"   - {dst}" for dst in local_files)
print(f"""
Project created at {dir_project_root}

Next steps:

1. Fill in real values in these files, copied from their examples
   (git-ignored, they never enter the repo):
{files}

2. Move the folder where you want it (optionally 'git init' there), then:

   cd {dir_project_root.name}
   mise run inst                   # fetches an AWS CodeArtifact token, then installs
   mise run cov                    # run the unit tests
   mise run lambda-layer-deploy    # build and publish the Lambda layer
   mise run cdk-up-dev-all         # deploy every stack to dev
""")
