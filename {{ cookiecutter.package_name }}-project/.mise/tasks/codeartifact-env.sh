# Source this file in any mise task that needs to authenticate with AWS CodeArtifact.
# It sets UV_INDEX_{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}_USERNAME and UV_INDEX_{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}_PASSWORD so uv can resolve private packages,
# both in the project's .venv (`inst`) and in the Lambda layer build (`lambda-layer-*`).
# Configuration variables (profile, domain, owner, region) are defined in mise.toml [env].
# Using --profile avoids polluting AWS_PROFILE in the environment.
# Token is valid for 12 hours (AWS default).
export UV_INDEX_{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}_USERNAME=aws

# In CI (GitHub Actions sets CI=true), credentials come from environment variables
# injected by aws-actions/configure-aws-credentials. No named profile exists.
# Locally, use the named AWS profile defined in AWS_CODEARTIFACT_PROFILE.
if [ -n "${CI:-}" ]; then
  PROFILE_FLAG=""
else
  PROFILE_FLAG="--profile $AWS_CODEARTIFACT_PROFILE"
fi

export UV_INDEX_{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}_PASSWORD=$(aws codeartifact get-authorization-token \
  $PROFILE_FLAG \
  --region $AWS_CODEARTIFACT_REGION \
  --domain $AWS_CODEARTIFACT_DOMAIN \
  --domain-owner $AWS_CODEARTIFACT_DOMAIN_OWNER \
  --query authorizationToken \
  --output text)

# `export` hides the exit code of the command above: stop here, not later on a uv 401.
if [ -z "$UV_INDEX_{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}_PASSWORD" ]; then
  echo "Failed to get an AWS CodeArtifact token (profile: ${AWS_CODEARTIFACT_PROFILE:-none}, domain: $AWS_CODEARTIFACT_DOMAIN)." >&2
  exit 1
fi
