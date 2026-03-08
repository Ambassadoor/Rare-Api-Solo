"""HTTP server for the Rare API."""

import os
import json

# from http.cookies import SimpleCookie
from http.server import HTTPServer
from dotenv import load_dotenv
from nss_handler import HandleRequests, status

load_dotenv()

# Add your imports below this line
from views.user import create_user, login_user, logout_user, get_user_info_from_token

origin = os.getenv("ALLOWED_ORIGIN")


class JSONServer(HandleRequests):
    """HTTP request handler for Rare API routes."""

    def _get_token(self):
        """Extracts the session token from the Cookie header.

        Returns:
            str | None: Session token if present, otherwise None
        """
        cookie_header = self.headers.get("Cookie", "")
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("token="):
                return part[len("token=") :]
        return None

    def _clear_auth_cookie(self, status_code, error, message):
        """Sends a JSON response and clears the auth cookie.

        Args:
            status_code (int): HTTP status code to return
            valid (bool): Value for the response body `{"valid": ...}`
        """
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header(
            "Set-Cookie", "token=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
        )
        self.end_headers()
        self.wfile.write(json.dumps({"error": error, "message": message}).encode())
        return

    def _require_auth(self):
        """Validates session token and returns authenticated user data.

        Returns:
            tuple[dict | None, bool]: `(user_data, handled)` where:
                - `user_data` is the authenticated user payload when valid
                - `handled` is True when this method already sent a 401 response
        """
        token = self._get_token()
        if not token:
            self._clear_auth_cookie(401, 'no_token', 'No active session token')
            return None, True

        user_json = get_user_info_from_token(token)
        user_data = json.loads(user_json)

        if user_data.get("valid") is False:
            self._clear_auth_cookie(401, 'session_expired', 'Session expired, please log in again')
            return None, True

        return user_data, False

    def do_GET(self):
        """Handle GET requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)
        requested_resource = url["requested_resource"]

        if requested_resource == "me":
            user, handled = self._require_auth()
            if handled:
                return

            return self.response(json.dumps(user), status.HTTP_200_SUCCESS.value)

        elif requested_resource == "user":
            # Example workflow for get user by id
            # if url["pk"] != 0:
            #     response_body = retrieve_user(url["pk"])
            #     return self.response(response_body, status.HTTP_200_SUCCESS.value)

            # response_body = list_users()
            # return self.response(response_body, status.HTTP_200_SUCCESS.value)
            return self.response("", status.HTTP_200_SUCCESS.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_PUT(self):
        """Handle PUT requests from a client"""

        # Parse the URL and get the primary key
        url = self.parse_url(self.path)
        pk = url["pk"]

        # Get the request body JSON for the new data
        content_len = int(self.headers.get("content-length", 0))
        request_body = self.rfile.read(content_len)
        request_body = json.loads(request_body)

        # Example of updating user info
        #     if url["requested_resource"] == "user":
        #         if pk != 0:
        #             successfully_updated = update_user(pk, request_body)
        #             if successfully_updated:
        #                 return self.response(
        #                     "", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
        #                 )

        return self.response(
            "Requested resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )

    def do_DELETE(self):
        """Handle DELETE requests from a client"""

        url = self.parse_url(self.path)
        pk = url["pk"]
        requested_resource = url["requested_resource"]

        if requested_resource == "user":
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )
        # Example of deleting a user
        #         if pk != 0:
        #             successfully_deleted = delete_user(pk)
        #             if successfully_deleted:
        #                 return self.response(
        #                     "", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
        #                 )

        #             return self.response(
        #                 "Requested resource not found",
        #                 status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        #             )
        elif requested_resource == "logout":
            token = self._get_token()

            if token:
                logout_user(token)

            self._clear_auth_cookie(200, None ,"User Successfully logged out")
            return

        else:
            return self.response(
                "Not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_POST(self):
        """Handle POST requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)

        content_len = int(self.headers.get("content-length", 0))
        request_body = self.rfile.read(content_len)
        request_body = json.loads(request_body)

        # Register a new user
        if url["requested_resource"] == "register":
            response_body = create_user(request_body)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.send_header(
                "Set-Cookie",
                f"token={response_body}; HttpOnly; SameSite=Lax; Path=/",
            )
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.end_headers()
            self.wfile.write((json.dumps({"valid": True}).encode()))
            return

        # Login a user
        elif url["requested_resource"] == "login":
            response_body = login_user(request_body)

            if response_body is not None:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Access-Control-Allow-Credentials", "true")
                self.send_header(
                    "Set-Cookie",
                    f"token={response_body}; HttpOnly; SameSite=Lax; Path=/",
                )
                self.end_headers()
                self.wfile.write((json.dumps({"valid": True}).encode()))
                return
            self.send_response(401)
            self.end_headers()
            return

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )


#
# THE CODE BELOW THIS LINE IS NOT IMPORTANT FOR REACHING YOUR LEARNING OBJECTIVES
#
def main():
    host = ""
    port = 8000
    HTTPServer((host, port), JSONServer).serve_forever()


if __name__ == "__main__":
    main()
