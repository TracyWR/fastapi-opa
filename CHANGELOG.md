# Change Log

## [1.3.0] - 2021-07-30

- Add slo and sls methods for saml auth.

## [1.2.1] - 2021-05-30

- Add readme flow diagram with absolute link to be displayed on pypi.

## [1.2.0] - 2021-05-29

- Add saml authentication as an authentication method.
- Adapt authentication interface (backwards compatible) to allow async and
  request usage within the authentication method.

## [1.1.0] - 2021-05-06

- Allow custom injectables to enrich the payload sent to OPA.
- Add GraphQLAnalysis to parse raw GraphQL payloads and add an injectable to
  send additional data to OPA allowing fine-grained authorization policies.

## [1.0.1] - 2021-04-25

- Remove uvicorn as a pkg dependency.
- Make OIDC jkws endpoint optional (not necessary for the HS256 algorithm).

## [1.0.0] - 2021-04-22

- Allow non-keycloak well_known endpoints and usage without a well_known
  endpoint. This changes the interface of the OIDC config object.
- Add support for python versions > 3.6.

## [0.1.1] - 2021-04-11

- Testing of OPA middleware and OIDC authentication as well as the
  pipeline setup for executing tests, style checks and dependency audit.
  ([#4](https://github.com/busykoala/fastapi-opa/pull/4))
  
## [0.1.0] - 2021-04-03

- Initial implementation of OPA middleware and OIDC authentication.
- Package documentation and usage instructions.
