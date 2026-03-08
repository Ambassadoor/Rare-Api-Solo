"""HTTP server for the Rare API."""

import os
import json
#from http.cookies import SimpleCookie
from http.server import HTTPServer
from dotenv import load_dotenv
from nss_handler import HandleRequests, status

load_dotenv()

# Add your imports below this line
from views.user import create_user, login_user, logout_user, get_user_info_from_token

origin = os.getenv("ALLOWED_ORIGIN")


class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for shipping ships"""

    def _get_token(self):
        """Parses the session token from the Cookie header

        Returns:
            str: Session token
        """
        cookie_header = self.headers.get("Cookie", "")
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("token="):
                return part[len("token="):]
        return None

    def _require_auth(self):
        """Checks for active session token

        Returns:
            json-string: {User data from current unexpired session, 401 response if no/expired session}
        """
        token = self._get_token()
        if not token:
            return None, self.response(json.dumps({"valid": False}), 401)

        user_json = get_user_info_from_token(token)
        if json.loads(user_json).get("valid") is False:
            return None, self.response(json.dumps({"valid": False}), 401)
        
        return json.loads(user_json), None
    
    def do_GET(self):
        """Handle GET requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)
        requested_resource = url["requested_resource"]

        if requested_resource == "me":
            token = self._get_token()

            if token:
                response_body = get_user_info_from_token(token)

                json_body = json.loads(response_body)

                if "valid" in json_body and json_body["valid"] is False:
                    return self.response(response_body, 401)

                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            return self.response(json.dumps({"valid": False}), 401)

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

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header(
                "Set-Cookie", "token=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
            )
            self.end_headers()
            self.wfile.write(json.dumps({"valid": False}).encode())
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
