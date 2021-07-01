from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import Union

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from pydantic.main import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_opa.auth.auth_interface import AuthInterface
from fastapi_opa.auth.exceptions import SAMLException


@dataclass
class SAMLConfig:
    settings_directory: str


class Userdata(BaseModel):
    samlUserdata: Dict
    samlNameId: str
    samlNameIdFormat: str
    samlNameIdNameQualifier: str
    samlNameIdSPNameQualifier: str
    samlSessionIndex: str


class SAMLAuthentication(AuthInterface):
    def __init__(self, config: SAMLConfig):
        self.config = config
        self.custom_folder = Path(self.config.settings_directory)

    async def authenticate(
        self, request: Request
    ) -> Union[RedirectResponse, Dict]:
        request_args = await self.prepare_request(request)
        auth = await self.init_saml_auth(request_args)

        if "acs" in request.query_params:
            print(datetime.utcnow(), '--acs--')
            return await self.assertion_consumer_service(auth, request_args)
        # potentially extend with logout here
        elif 'sso' in request.query_params:
            print(datetime.utcnow(), '--sso--')
            return await self.single_sign_on(auth)
            # TODO: check below code
            # If AuthNRequest ID need to be stored in order to later validate it, do instead
            # sso_built_url = auth.login()
            # request.session['AuthNRequestID'] = auth.get_last_request_id()
            # return redirect(sso_built_url)
        elif 'sso2' in request.query_params:
            print(datetime.utcnow(), '--sso2--')
            return_to = '%sattrs/' % request.base_url
            return RedirectResponse(auth.login(return_to))
        elif 'slo' in request.query_params:
            print(datetime.utcnow(), '--slo--')
            return await self.single_log_out(auth)
        # TODO: handle sls
        # elif 'sls' in request.query_params:
        #     print(datetime.utcnow(), '--sls--')
        #     request_id = None
        #     if 'LogoutRequestID' in request.query_params['post_data']:
        #         request_id = req_args['post_data']['LogoutRequestID']
        #     # TODO: not sure how to handle session here
        #     dscb = lambda: request.session.flush()
        #     url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        #     errors = auth.get_errors()
        #     if len(errors) == 0:
        #         if url is not None:
        #             return RedirectResponse(url)
        #         else:
        #             success_slo = True
        #     elif auth.get_settings().is_debug_active():
        #         error_reason = auth.get_last_error_reason()
        return await self.single_sign_on(auth)

    async def init_saml_auth(self, request_args: Dict) -> OneLogin_Saml2_Auth:
        return OneLogin_Saml2_Auth(
            request_args, custom_base_path=self.custom_folder.as_posix()
        )

    @staticmethod
    async def single_log_out(auth: OneLogin_Saml2_Auth) -> RedirectResponse:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if auth.get_nameid():
            name_id = auth.get_nameid()
        if auth.get_session_index():
            session_index = auth.get_session_index()
        if auth.get_nameid_format():
            name_id_format = auth.get_nameid_format()
        if auth.get_nameid_spnq():
            name_id_spnq = auth.get_nameid_spnq()
        if auth.get_nameid_nq():
            name_id_nq = auth.get_nameid_nq()
        return RedirectResponse(
            auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format,
                        spnq=name_id_spnq))

    @staticmethod
    async def single_sign_on(auth: OneLogin_Saml2_Auth) -> RedirectResponse:
        redirect_url = auth.login()
        return RedirectResponse(redirect_url)

    @staticmethod
    async def assertion_consumer_service(
        auth: OneLogin_Saml2_Auth, request_args: Dict
    ) -> Union[RedirectResponse, Userdata]:
        auth.process_response()
        errors = auth.get_errors()
        if not len(errors) == 0:
            raise SAMLException()
        userdata = {
            "samlUserdata": auth.get_attributes(),
            "samlNameId": auth.get_nameid(),
            "samlNameIdFormat": auth.get_nameid_format(),
            "samlNameIdNameQualifier": auth.get_nameid_nq(),
            "samlNameIdSPNameQualifier": auth.get_nameid_spnq(),
            "samlSessionIndex": auth.get_session_index(),
        }

        self_url = OneLogin_Saml2_Utils.get_self_url(request_args)
        if "RelayState" in request_args.get("post_data") and self_url.rstrip(
            "/"
        ) != request_args.get("post_data", {}).get("RelayState").rstrip("/"):
            return RedirectResponse(
                auth.redirect_to(
                    request_args.get("post_data", {}).get("RelayState")
                )
            )
        else:
            return userdata

    @staticmethod
    async def prepare_request(request: Request):
        return {
            "https": "on" if request.url.scheme == "https" else "off",
            "http_host": request.url.hostname,
            "server_port": request.url.port,
            "script_name": request.url.path,
            "post_data": await request.form()
            # Uncomment if using ADFS
            # "lowercase_urlencoding": True
        }
